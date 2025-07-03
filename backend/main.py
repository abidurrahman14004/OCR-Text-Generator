import time
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  


CORS(app, 
     origins=['http://localhost:3000', 'http://localhost:5173', 'http://127.0.0.1:5173'],
     methods=['GET', 'POST', 'OPTIONS'],
     allow_headers=['Content-Type'])


UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


try:
    from services.service import OCRSpaceService
    
    api_key = os.getenv('OCRSPACE_API_KEY', 'helloworld')  
    ocr_service = OCRSpaceService(api_key=api_key)
    logger.info("OCR.space Service initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize OCR.space service: {str(e)}")
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
        'ocr_service': 'OCR.space API'
    })

@app.route('/api/extract-text', methods=['POST', 'OPTIONS'])
def extract_text():
    """OCR text extraction endpoint using OCR.space"""
 
    if request.method == 'OPTIONS':
        return '', 200
    
    logger.info("🔍 OCR.space endpoint called!")
    
    try:
  
        if not ocr_service:
            logger.error("OCR.space service not initialized")
            return jsonify({
                'success': False,
                'error': 'OCR service not available. Check server configuration.'
            }), 500

   
        if 'file' not in request.files:
            logger.warning("❌ No file in request")
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400

        file = request.files['file']
        logger.info(f"📁 Received file: {file.filename}")
        
 
        if file.filename == '':
            logger.warning("❌ No file selected")
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400


        if not allowed_file(file.filename, ALLOWED_EXTENSIONS):
            logger.warning(f"❌ Invalid file type: {file.filename}")
            return jsonify({
                'success': False,
                'error': 'Invalid file type. Allowed: ' + ', '.join(ALLOWED_EXTENSIONS)
            }), 400

   
        filename = secure_filename(file.filename)
        timestamp = str(int(time.time()))
        unique_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        file.save(file_path)
        logger.info(f"💾 File saved: {file_path}")
        

        file_size = os.path.getsize(file_path)
        if file_size > 1024 * 1024:  # 1MB
            logger.warning(f"File size too large: {file_size} bytes")

        
        logger.info(f"🚀 Processing OCR with OCR.space for: {unique_filename}")
        

        try:
            result = ocr_service.extract_and_correct_text(file_path)
            logger.info(f"OCR.space processing result: {result.get('success', False)}")
        except Exception as ocr_error:
            logger.error(f"OCR.space processing failed: {str(ocr_error)}")
            result = {
                'success': False,
                'error': f'OCR processing failed: {str(ocr_error)}'
            }
   
        try:
            os.remove(file_path)
            logger.info(f"🗑️ Cleaned up temporary file: {file_path}")
        except Exception as cleanup_error:
            logger.warning(f"Failed to cleanup file: {cleanup_error}")
        
        if result.get('success', False):
            extracted_text = result.get('extracted_text', result.get('corrected_text', ''))
            logger.info(f"✅ OCR completed successfully. Text length: {len(extracted_text)}")
            
   
            response_data = {
                'success': True,
                'extracted_text': extracted_text,
                'corrected_text': extracted_text,
                'original_text': result.get('raw_text', result.get('original_text', '')),
                'raw_text': result.get('raw_text', result.get('original_text', '')),
                'corrections': result.get('corrections', []),
                'statistics': result.get('statistics', {}),
                'confidence': result.get('confidence', 0.8),
                'processing_time': result.get('processing_time', 0),
                'ocr_service': 'OCR.space API'
            }
            
          
            if not extracted_text.strip():
                return jsonify({
                    'success': False,
                    'error': 'No text found in the image. Please try with a clearer image containing readable text.'
                }), 400
            
            return jsonify(response_data)
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

@app.route('/api/correct-text', methods=['POST', 'OPTIONS'])
def correct_text():
    """Text correction endpoint"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        if not ocr_service:
            return jsonify({
                'success': False,
                'error': 'OCR service not available'
            }), 500

        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'success': False,
                'error': 'No text provided'
            }), 400

        raw_text = data['text']
        
        if not raw_text.strip():
            return jsonify({
                'success': False,
                'error': 'Empty text provided'
            }), 400

        logger.info(f"Processing text correction. Text length: {len(raw_text)}")
        

        result = ocr_service.correct_text_only(raw_text)
        
        if result.get('success', False):
            return jsonify({
                'success': True,
                'corrected_text': result.get('corrected_text', raw_text),
                'corrections': result.get('corrections', []),
                'statistics': result.get('statistics', {}),
                'confidence': result.get('confidence', 0.8)
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Text correction failed')
            }), 500

    except Exception as e:
        logger.error(f"Text correction error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to correct text: {str(e)}'
        }), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get server status and capabilities"""
    service_info = ocr_service.get_service_info() if ocr_service else {}
    
    return jsonify({
        'status': 'running',
        'ocr_service': 'OCR.space API',
        'ocr_service_ready': ocr_service is not None,
        'supported_formats': list(ALLOWED_EXTENSIONS),
        'max_file_size': '16MB (server) / 1MB (OCR.space free tier)',
        'version': '2.0.0',
        'service_details': service_info
    })

@app.route('/api/api-info', methods=['GET'])
def get_api_info():
    """Get OCR.space API information and usage"""
    if not ocr_service:
        return jsonify({
            'error': 'OCR service not available'
        }), 500
    
    return jsonify({
        'service': 'OCR.space API',
        'free_tier_limit': '25,000 requests/month',
        'file_size_limit': '1MB (free) / 5MB (paid)',
        'supported_languages': ['English', 'Arabic', 'Chinese (Simplified)', 'Chinese (Traditional)', 'Czech', 'Danish', 'Dutch', 'Finnish', 'French', 'German', 'Greek', 'Hungarian', 'Korean', 'Italian', 'Japanese', 'Polish', 'Portuguese', 'Russian', 'Slovenian', 'Spanish', 'Swedish', 'Turkish'],
        'features': [
            'High accuracy OCR',
            'Multiple language support', 
            'Automatic orientation detection',
            'Table detection',
            'PDF support',
            'Intelligent text correction'
        ],
        'api_key_configured': len(ocr_service.api_key) > 10 if ocr_service else False
    })

@app.errorhandler(413)
def file_too_large(error):
    """Handle file too large error"""
    return jsonify({
        'success': False,
        'error': 'File too large. Maximum size is 16MB (server limit). OCR.space free tier supports up to 1MB.'
    }), 413

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    """Handle method not allowed errors"""
    return jsonify({
        'success': False,
        'error': 'Method not allowed for this endpoint'
    }), 405

@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors"""
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
            logger.info("💡 For higher limits, set OCRSPACE_API_KEY environment variable")
        else:
            logger.info("🔑 Using custom OCR.space API key")
    
    # Run the app
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        threaded=True
    )