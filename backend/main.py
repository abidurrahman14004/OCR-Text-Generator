import time
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import logging
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  

# CORS setup
CORS(app, 
     origins=['*'],
     methods=['GET', 'POST', 'OPTIONS'],
     allow_headers=['Content-Type'])

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# OCR Service Class - Embedded directly in main.py
class OCRSpaceService:
    def __init__(self, api_key='helloworld'):
        self.api_key = api_key
        self.api_url = 'https://api.ocr.space/parse/image'
        logger.info(f"OCR.space service initialized with API key")
    
    def extract_and_correct_text(self, image_path):
        try:
            logger.info(f"Starting OCR processing for: {image_path}")
            
            with open(image_path, 'rb') as image_file:
                files = {'file': image_file}
                data = {
                    'apikey': self.api_key,
                    'language': 'eng',
                    'OCREngine': 2,
                    'detectOrientation': True,
                    'isOverlayRequired': False
                }
                
                response = requests.post(self.api_url, files=files, data=data, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get('IsErroredOnProcessing', True):
                        error_msg = result.get('ErrorMessage', ['Unknown error'])
                        if isinstance(error_msg, list):
                            error_msg = ', '.join(error_msg)
                        logger.error(f"OCR.space error: {error_msg}")
                        return {'success': False, 'error': f'OCR error: {error_msg}'}
                    
                    # Extract text
                    extracted_text = ""
                    parsed_results = result.get('ParsedResults', [])
                    
                    for parsed_result in parsed_results:
                        text = parsed_result.get('ParsedText', '')
                        if text:
                            extracted_text += text
                    
                    extracted_text = extracted_text.strip()
                    
                    if not extracted_text:
                        return {'success': False, 'error': 'No text found in image'}
                    
                    logger.info(f"OCR completed successfully. Text length: {len(extracted_text)}")
                    
                    return {
                        'success': True,
                        'extracted_text': extracted_text,
                        'corrected_text': extracted_text,
                        'raw_text': extracted_text,
                        'original_text': extracted_text,
                        'corrections': [],
                        'confidence': 0.8,
                        'statistics': {
                            'raw_word_count': len(extracted_text.split()),
                            'corrected_word_count': len(extracted_text.split()),
                            'corrections_applied': 0,
                            'quality_assessment': 'Good'
                        },
                        'processing_time': 1.0
                    }
                else:
                    logger.error(f"OCR API request failed: {response.status_code}")
                    return {'success': False, 'error': f'API request failed: {response.status_code}'}
                    
        except requests.exceptions.Timeout:
            logger.error("OCR API timeout")
            return {'success': False, 'error': 'OCR timeout. Try a smaller image.'}
        except Exception as e:
            logger.error(f"OCR processing error: {str(e)}")
            return {'success': False, 'error': f'OCR error: {str(e)}'}
    
    def correct_text_only(self, text):
        return {
            'success': True,
            'corrected_text': text,
            'corrections': [],
            'confidence': 0.8,
            'statistics': {'raw_word_count': len(text.split())}
        }
    
    def get_service_info(self):
        return {'service': 'OCR.space', 'ready': True}

# Initialize OCR service
try:
    api_key = os.getenv('OCRSPACE_API_KEY', 'helloworld')
    ocr_service = OCRSpaceService(api_key=api_key)
    logger.info("✅ OCR.space Service initialized successfully!")
except Exception as e:
    logger.error(f"❌ Failed to initialize OCR.space service: {str(e)}")
    ocr_service = None

def allowed_file(filename, allowed_extensions):
    """Check if the uploaded file has an allowed extension"""
    if not filename:
        return False
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@app.route('/')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'OCR Backend Server is running',
        'version': '2.0.0',
        'ocr_service': 'OCR.space API',
        'ocr_service_ready': ocr_service is not None
    })

@app.route('/api/test', methods=['POST', 'OPTIONS'])
def test_endpoint():
    """Simple test endpoint to verify connection"""
    if request.method == 'OPTIONS':
        return '', 200
    
    logger.info("✅ Test endpoint called successfully!")
    return jsonify({
        'success': True,
        'message': 'Backend connection working with OCR.space!',
        'timestamp': time.time(),
        'ocr_service': 'OCR.space API',
        'service_ready': ocr_service is not None
    })

@app.route('/api/extract-text', methods=['POST', 'OPTIONS'])
def extract_text():
    """OCR text extraction endpoint using OCR.space"""
    if request.method == 'OPTIONS':
        return '', 200
    
    logger.info("🔍 OCR.space endpoint called!")
    
    try:
        # Check if OCR service is available
        if not ocr_service:
            logger.error("❌ OCR.space service not initialized")
            return jsonify({
                'success': False,
                'error': 'OCR service not available. Service initialization failed.'
            }), 500

        # Check if file is in request
        if 'file' not in request.files:
            logger.warning("❌ No file in request")
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400

        file = request.files['file']
        logger.info(f"📁 Received file: {file.filename}")
        
        # Check if file is selected
        if file.filename == '':
            logger.warning("❌ No file selected")
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400

        # Validate file type
        if not allowed_file(file.filename, ALLOWED_EXTENSIONS):
            logger.warning(f"❌ Invalid file type: {file.filename}")
            return jsonify({
                'success': False,
                'error': 'Invalid file type. Allowed: ' + ', '.join(ALLOWED_EXTENSIONS)
            }), 400

        # Save temporary file
        filename = secure_filename(file.filename)
        timestamp = str(int(time.time()))
        unique_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        file.save(file_path)
        logger.info(f"💾 File saved: {file_path}")
        
        # Process OCR
        logger.info(f"🚀 Processing OCR with OCR.space for: {unique_filename}")
        
        result = ocr_service.extract_and_correct_text(file_path)
        
        # Cleanup temporary file
        try:
            os.remove(file_path)
            logger.info(f"🗑️ Cleaned up temporary file: {file_path}")
        except Exception as cleanup_error:
            logger.warning(f"Failed to cleanup file: {cleanup_error}")
        
        if result.get('success', False):
            extracted_text = result.get('extracted_text', '')
            logger.info(f"✅ OCR completed successfully. Text length: {len(extracted_text)}")
            
            if not extracted_text.strip():
                return jsonify({
                    'success': False,
                    'error': 'No text found in the image. Please try with a clearer image.'
                }), 400
            
            return jsonify(result)
        else:
            error_msg = result.get('error', 'Unknown OCR processing error')
            logger.error(f"❌ OCR.space failed: {error_msg}")
            return jsonify({
                'success': False,
                'error': error_msg
            }), 500

    except Exception as e:
        logger.error(f"❌ OCR extraction error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get server status and capabilities"""
    return jsonify({
        'status': 'running',
        'ocr_service': 'OCR.space API',
        'ocr_service_ready': ocr_service is not None,
        'supported_formats': list(ALLOWED_EXTENSIONS),
        'max_file_size': '16MB (server) / 1MB (OCR.space free tier)',
        'version': '2.0.0'
    })

@app.errorhandler(413)
def file_too_large(error):
    return jsonify({
        'success': False,
        'error': 'File too large. Maximum size is 16MB.'
    }), 413

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    logger.info("🚀 Starting OCR Backend Server with OCR.space...")
    logger.info(f"📁 Upload folder: {UPLOAD_FOLDER}")
    logger.info(f"📋 Allowed extensions: {ALLOWED_EXTENSIONS}")
    logger.info(f"🔧 OCR.space Service ready: {ocr_service is not None}")
    
    if ocr_service:
        api_key = os.getenv('OCRSPACE_API_KEY', 'helloworld')
        if api_key == 'helloworld':
            logger.info("🆓 Using OCR.space free tier (25,000 requests/month)")
        else:
            logger.info("🔑 Using custom OCR.space API key")
    
    # Run the app
    port = int(os.environ.get('PORT', 5000))
    app.run(
        debug=False,
        host='0.0.0.0',
        port=port,
        threaded=True
    )