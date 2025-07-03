import time
import requests
import logging
from typing import Dict, Any
import os
from model.intelligent_corrector import IntelligentOCRCorrector

logger = logging.getLogger(__name__)

class OCRSpaceService:
    """
    OCR Service using OCR.space API with intelligent text correction
    """
    
    def __init__(self, api_key: str = None):
        """Initialize OCR.space service"""
        # Get API key from environment or use free tier
        self.api_key = api_key or os.getenv('OCRSPACE_API_KEY', 'helloworld')  # Free tier key
        self.api_url = 'https://api.ocr.space/parse/image'
        
        # Initialize intelligent corrector
        try:
            self.corrector = IntelligentOCRCorrector()
            logger.info("Intelligent corrector initialized")
        except Exception as e:
            logger.error(f"Failed to initialize corrector: {str(e)}")
            self.corrector = None
        
        logger.info(f"OCR.space service initialized (API Key: {'***' + self.api_key[-4:] if len(self.api_key) > 4 else 'FREE'})")
    
    def extract_text_with_ocrspace(self, image_path: str) -> Dict[str, Any]:
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
                
                return {
                    'success': True,
                    'text': extracted_text,
                    'processing_time': processing_time,
                    'character_count': len(extracted_text),
                    'word_count': len(extracted_text.split()) if extracted_text else 0,
                    'api_response': result  # Include full response for debugging
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
    
    def extract_and_correct_text(self, image_path: str) -> Dict[str, Any]:
        """
        Main method to extract and intelligently correct text from image
        """
        try:
            start_time = time.time()
            logger.info(f"Starting OCR + correction process for: {image_path}")
            
            # Extract raw text using OCR.space
            ocr_result = self.extract_text_with_ocrspace(image_path)
            
            if not ocr_result['success']:
                return ocr_result
            
            raw_text = ocr_result['text']
            
            if not raw_text.strip():
                return {
                    'success': False,
                    'error': 'No text found in image'
                }
            
            # Apply intelligent corrections if corrector is available
            if self.corrector:
                logger.info("Applying intelligent text corrections...")
                correction_result = self.corrector.comprehensive_correction(raw_text)
                
                if correction_result.get('success', False):
                    corrected_text = correction_result['corrected_text']
                    corrections = correction_result['corrections']
                    confidence = correction_result['confidence']
                else:
                    # If correction fails, use raw text
                    logger.warning("Text correction failed, using raw OCR text")
                    corrected_text = raw_text
                    corrections = []
                    confidence = 0.6
            else:
                # No corrector available, use raw text
                corrected_text = raw_text
                corrections = []
                confidence = 0.5
            
            total_processing_time = time.time() - start_time
            
            # Calculate statistics
            statistics = self.calculate_statistics(raw_text, corrected_text, corrections)
            
            logger.info(f"Complete OCR + correction process finished in {total_processing_time:.2f}s")
            logger.info(f"Applied {len(corrections)} corrections")
            
            return {
                'success': True,
                'extracted_text': corrected_text,
                'corrected_text': corrected_text,
                'raw_text': raw_text,
                'original_text': raw_text,
                'corrections': corrections,
                'confidence': confidence,
                'statistics': statistics,
                'processing_time': total_processing_time,
                'ocr_method': 'OCR.space API',
                'api_response': ocr_result.get('api_response', {})
            }
            
        except Exception as e:
            logger.error(f"OCR and correction process failed: {str(e)}")
            return {
                'success': False,
                'error': f'Processing failed: {str(e)}'
            }
    
    def correct_text_only(self, raw_text: str) -> Dict[str, Any]:
        """
        Apply intelligent corrections to already extracted text
        """
        try:
            start_time = time.time()
            
            if not raw_text.strip():
                return {
                    'success': False,
                    'error': 'Empty text provided'
                }
            
            if not self.corrector:
                return {
                    'success': True,
                    'corrected_text': raw_text,
                    'corrections': [],
                    'confidence': 0.5,
                    'statistics': {'message': 'No text corrector available'},
                    'processing_time': 0
                }
            
            # Apply intelligent corrections
            correction_result = self.corrector.comprehensive_correction(raw_text)
            
            processing_time = time.time() - start_time
            
            if correction_result.get('success', False):
                corrected_text = correction_result['corrected_text']
                corrections = correction_result['corrections']
                confidence = correction_result['confidence']
            else:
                # Return original text if correction fails
                corrected_text = raw_text
                corrections = []
                confidence = 0.5
            
            # Calculate statistics
            statistics = self.calculate_statistics(raw_text, corrected_text, corrections)
            
            logger.info(f"Text correction completed in {processing_time:.2f}s")
            
            return {
                'success': True,
                'corrected_text': corrected_text,
                'corrections': corrections,
                'confidence': confidence,
                'statistics': statistics,
                'processing_time': processing_time
            }
            
        except Exception as e:
            logger.error(f"Text correction failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def calculate_statistics(self, raw_text: str, corrected_text: str, corrections: list) -> Dict[str, Any]:
        """
        Calculate statistics about the OCR and correction process
        """
        try:
            raw_words = raw_text.split() if raw_text else []
            corrected_words = corrected_text.split() if corrected_text else []
            
            # Basic statistics
            stats = {
                'raw_character_count': len(raw_text),
                'corrected_character_count': len(corrected_text),
                'raw_word_count': len(raw_words),
                'corrected_word_count': len(corrected_words),
                'raw_line_count': len(raw_text.split('\n')) if raw_text else 0,
                'corrected_line_count': len(corrected_text.split('\n')) if corrected_text else 0,
                'corrections_applied': len(corrections),
                'correction_rate': 0
            }
            
            # Calculate correction rate
            if stats['raw_word_count'] > 0:
                stats['correction_rate'] = round(
                    (stats['corrections_applied'] / stats['raw_word_count']) * 100, 2
                )
            
            # Group corrections by method
            correction_methods = {}
            for correction in corrections:
                method = correction.get('method', 'unknown')
                if method not in correction_methods:
                    correction_methods[method] = 0
                correction_methods[method] += 1
            
            stats['correction_methods'] = correction_methods
            
            # Quality assessment
            if stats['corrections_applied'] == 0:
                stats['quality_assessment'] = "Excellent - No corrections needed"
            elif stats['correction_rate'] < 10:
                stats['quality_assessment'] = "Very Good - Minor corrections"
            elif stats['correction_rate'] < 20:
                stats['quality_assessment'] = "Good - Some corrections applied"
            elif stats['correction_rate'] < 40:
                stats['quality_assessment'] = "Fair - Multiple corrections needed"
            else:
                stats['quality_assessment'] = "Challenging - Many corrections applied"
            
            return stats
            
        except Exception as e:
            logger.error(f"Statistics calculation failed: {str(e)}")
            return {
                'error': 'Failed to calculate statistics',
                'raw_word_count': len(raw_text.split()) if raw_text else 0,
                'corrected_word_count': len(corrected_text.split()) if corrected_text else 0,
                'corrections_applied': len(corrections)
            }
    
    def get_service_info(self) -> Dict[str, Any]:
        """
        Get information about the OCR service
        """
        return {
            'ocr_service': 'OCR.space API',
            'api_url': self.api_url,
            'has_api_key': len(self.api_key) > 10,  # Check if using real API key
            'correction_available': self.corrector is not None,
            'correction_methods': self.corrector.get_available_methods() if self.corrector else [],
            'supported_formats': ['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'gif', 'pdf'],
            'max_image_size': '1MB (free tier) / 5MB (paid)',
            'languages_supported': ['eng', 'ara', 'chs', 'cht', 'cze', 'dan', 'dut', 'fin', 'fre', 'ger', 'gre', 'hun', 'kor', 'ita', 'jpn', 'pol', 'por', 'rus', 'slv', 'spa', 'swe', 'tur']
        }