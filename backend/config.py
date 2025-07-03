import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class"""
    
    # Flask Settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    TESTING = False
    
    # File Upload Settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}
    
    # OCR Settings
    OCR_LANGUAGES = ['en']  # Supported languages
    OCR_GPU_ENABLED = os.environ.get('OCR_GPU_ENABLED', 'true').lower() == 'true'
    
    # Text Correction Settings
    ENABLE_SPELL_CHECK = os.environ.get('ENABLE_SPELL_CHECK', 'true').lower() == 'true'
    ENABLE_FUZZY_MATCHING = os.environ.get('ENABLE_FUZZY_MATCHING', 'true').lower() == 'true'
    ENABLE_CONTEXT_CORRECTION = os.environ.get('ENABLE_CONTEXT_CORRECTION', 'false').lower() == 'true'
    
    # File Cleanup Settings
    CLEANUP_INTERVAL_HOURS = int(os.environ.get('CLEANUP_INTERVAL_HOURS', '24'))
    AUTO_CLEANUP_ENABLED = os.environ.get('AUTO_CLEANUP_ENABLED', 'true').lower() == 'true'
    
    # CORS Settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5173').split(',')
    
    # Logging Settings
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'ocr_backend.log')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    
    # Security headers for production
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block'
    }

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    UPLOAD_FOLDER = 'test_uploads'
    AUTO_CLEANUP_ENABLED = False

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}