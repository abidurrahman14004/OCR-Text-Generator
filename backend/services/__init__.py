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