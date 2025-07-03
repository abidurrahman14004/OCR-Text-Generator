from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

def handler(req):
    # Handle CORS
    if req.method == 'OPTIONS':
        return ('', 200, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
        })
    
    try:
        # Get file from request
        file = req.files.get('file')
        if not file:
            return (json.dumps({'success': False, 'error': 'No file provided'}), 400, {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            })
        
        # OCR with OCR.space
        files = {'file': file}
        data = {
            'apikey': 'helloworld',
            'language': 'eng',
            'OCREngine': 2
        }
        
        response = requests.post('https://api.ocr.space/parse/image', 
                               files=files, data=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if not result.get('IsErroredOnProcessing', True):
                text = ""
                for parsed in result.get('ParsedResults', []):
                    text += parsed.get('ParsedText', '')
                
                return (json.dumps({
                    'success': True,
                    'extracted_text': text.strip(),
                    'original_text': text.strip(),
                    'corrections': [],
                    'confidence': 0.8,
                    'statistics': {'raw_word_count': len(text.split())}
                }), 200, {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                })
        
        return (json.dumps({'success': False, 'error': 'OCR processing failed'}), 500, {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json'
        })
        
    except Exception as e:
        return (json.dumps({'success': False, 'error': f'Server error: {str(e)}'}), 500, {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json'
        })