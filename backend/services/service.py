import requests
import os
import time
import logging

logger = logging.getLogger(__name__)

class OCRSpaceService:
    """
    OCR Service using OCR.space API
    """
    
    def __init__(self, api_key='helloworld'):
        """Initialize OCR.space service"""
        self.api_key = api_key
        self.api_url = 'https://api.ocr.space/parse/image'
        
        logger.info(f"OCR.space service initialized (API Key: ***{api_key[-4:] if len(api_key) > 4 else 'FREE'})")
    
    def extract_and_correct_text(self, image_path):
        """
        Extract text from image using OCR.space API
        """
        try:
            start_time = time.time()
            logger.info(f"Starting OCR.space processing for: {image_path}")
            
            # Prepare the request
            with open(image_path, 'rb') as image_file:
                files = {'file': image_file}
                
                data = {
                    'apikey': self.api_key,
                    'language': 'eng',
                    'isOverlayRequired': False,
                    'detectOrientation': True,
                    'isTable': False,
                    'scale': True,
                    'OCREngine': 2  # Use OCR Engine 2 for better accuracy
                }
                
                # Make API request
                response = requests.post(self.api_url, files=files, data=data, timeout=30)
            
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('IsErroredOnProcessing', True):
                    error_msg = result.get('ErrorMessage', ['Unknown OCR error'])
                    if isinstance(error_msg, list):
                        error_msg = ', '.join(error_msg)
                    
                    logger.error(f"OCR.space API error: {error_msg}")
                    return {
                        'success': False,
                        'error': f'OCR processing failed: {error_msg}'
                    }
                
                # Extract text from response
                extracted_text = ""
                parsed_results = result.get('ParsedResults', [])
                
                if parsed_results:
                    for parsed_result in parsed_results:
                        text = parsed_result.get('ParsedText', '')
                        if text:
                            extracted_text += text + '\n'
                
                extracted_text = extracted_text.strip()
                
                if not extracted_text:
                    return {
                        'success': False,
                        'error': 'No text found in the image'
                    }
                
                logger.info(f"OCR.space extraction completed in {processing_time:.2f}s")
                logger.info(f"Extracted {len(extracted_text)} characters")
                
                # Calculate statistics
                statistics = {
                    'raw_character_count': len(extracted_text),
                    'corrected_character_count': len(extracted_text),
                    'raw_word_count': len(extracted_text.split()) if extracted_text else 0,
                    'corrected_word_count': len(extracted_text.split()) if extracted_text else 0,
                    'raw_line_count': len(extracted_text.split('\n')) if extracted_text else 0,
                    'corrected_line_count': len(extracted_text.split('\n')) if extracted_text else 0,
                    'corrections_applied': 0,
                    'correction_rate': 0,
                    'quality_assessment': "Good - OCR.space processing"
                }
                
                return {
                    'success': True,
                    'extracted_text': extracted_text,
                    'corrected_text': extracted_text,
                    'raw_text': extracted_text,
                    'original_text': extracted_text,
                    'corrections': [],
                    'confidence': 0.8,
                    'statistics': statistics,
                    'processing_time': processing_time,
                    'ocr_method': 'OCR.space API',
                    'api_response': result
                }
            
            else:
                logger.error(f"OCR.space API request failed: {response.status_code}")
                return {
                    'success': False,
                    'error': f'API request failed with status code: {response.status_code}'
                }
                
        except requests.exceptions.Timeout:
            logger.error("OCR.space API timeout")
            return {
                'success': False,
                'error': 'OCR processing timeout. Please try again with a smaller image.'
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"OCR.space API request error: {str(e)}")
            return {
                'success': False,
                'error': f'Network error: {str(e)}'
            }
        except Exception as e:
            logger.error(f"OCR.space processing error: {str(e)}")
            return {
                'success': False,
                'error': f'OCR processing failed: {str(e)}'
            }
    
    def correct_text_only(self, raw_text):
        """
        Apply basic corrections to already extracted text
        """
        try:
            start_time = time.time()
            
            if not raw_text.strip():
                return {
                    'success': False,
                    'error': 'Empty text provided'
                }
            
            # For now, just return the text as-is
            # You can add basic text cleaning here if needed
            corrected_text = raw_text.strip()
            
            processing_time = time.time() - start_time
            
            # Calculate basic statistics
            statistics = {
                'raw_character_count': len(raw_text),
                'corrected_character_count': len(corrected_text),
                'raw_word_count': len(raw_text.split()) if raw_text else 0,
                'corrected_word_count': len(corrected_text.split()) if corrected_text else 0,
                'corrections_applied': 0,
                'correction_rate': 0,
                'quality_assessment': "Good - No corrections needed"
            }
            
            logger.info(f"Text correction completed in {processing_time:.2f}s")
            
            return {
                'success': True,
                'corrected_text': corrected_text,
                'corrections': [],
                'confidence': 0.8,
                'statistics': statistics,
                'processing_time': processing_time
            }
            
        except Exception as e:
            logger.error(f"Text correction failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_service_info(self):
        """
        Get information about the OCR service
        """
        return {
            'ocr_service': 'OCR.space API',
            'api_url': self.api_url,
            'has_api_key': len(self.api_key) > 10,
            'supported_formats': ['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'gif', 'pdf'],
            'max_image_size': '1MB (free tier) / 5MB (paid)',
            'languages_supported': ['eng', 'ara', 'chs', 'cht', 'cze', 'dan', 'dut', 'fin', 'fre', 'ger', 'gre', 'hun', 'kor', 'ita', 'jpn', 'pol', 'por', 'rus', 'slv', 'spa', 'swe', 'tur'],
            'features': [
                'High accuracy OCR',
                'Multiple language support',
                'Automatic orientation detection',
                'Table detection',
                'PDF support'
            ]
        }