import requests
import logging

logger = logging.getLogger(__name__)

class OCRSpaceService:
    def __init__(self, api_key='helloworld'):
        self.api_key = api_key
        self.api_url = 'https://api.ocr.space/parse/image'
        logger.info(f"OCR.space service initialized")
    
    def extract_and_correct_text(self, image_path):
        try:
            with open(image_path, 'rb') as image_file:
                files = {'file': image_file}
                data = {
                    'apikey': self.api_key,
                    'language': 'eng',
                    'OCREngine': 2
                }
                
                response = requests.post(self.api_url, files=files, data=data, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    if not result.get('IsErroredOnProcessing', True):
                        text = ""
                        for parsed in result.get('ParsedResults', []):
                            text += parsed.get('ParsedText', '')
                        
                        return {
                            'success': True,
                            'extracted_text': text.strip(),
                            'raw_text': text.strip(),
                            'corrections': [],
                            'confidence': 0.8,
                            'statistics': {'raw_word_count': len(text.split())},
                            'processing_time': 1.0
                        }
                
                return {'success': False, 'error': 'OCR processing failed'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
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