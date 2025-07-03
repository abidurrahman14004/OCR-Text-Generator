import os
import time
import logging
from typing import Set

logger = logging.getLogger(__name__)

def allowed_file(filename: str, allowed_extensions: Set[str]) -> bool:
    """
    Check if the uploaded file has an allowed extension
    
    Args:
        filename: Name of the file
        allowed_extensions: Set of allowed file extensions
        
    Returns:
        True if file extension is allowed, False otherwise
    """
    if not filename:
        return False
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def get_file_extension(filename: str) -> str:
    """
    Get file extension from filename
    
    Args:
        filename: Name of the file
        
    Returns:
        File extension in lowercase
    """
    if not filename or '.' not in filename:
        return ''
    
    return filename.rsplit('.', 1)[1].lower()

def get_file_size_mb(file_path: str) -> float:
    """
    Get file size in megabytes
    
    Args:
        file_path: Path to the file
        
    Returns:
        File size in MB
    """
    try:
        size_bytes = os.path.getsize(file_path)
        return round(size_bytes / (1024 * 1024), 2)
    except:
        return 0.0

def cleanup_old_files(upload_folder: str, max_age_hours: int = 24) -> int:
    """
    Clean up old files from upload folder
    
    Args:
        upload_folder: Path to upload folder
        max_age_hours: Maximum age of files in hours before deletion
        
    Returns:
        Number of files deleted
    """
    try:
        if not os.path.exists(upload_folder):
            return 0
        
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        deleted_count = 0
        
        for filename in os.listdir(upload_folder):
            file_path = os.path.join(upload_folder, filename)
            
            if os.path.isfile(file_path):
                file_age = current_time - os.path.getmtime(file_path)
                
                if file_age > max_age_seconds:
                    try:
                        os.remove(file_path)
                        deleted_count += 1
                        logger.info(f"Deleted old file: {filename}")
                    except Exception as e:
                        logger.warning(f"Failed to delete file {filename}: {str(e)}")
        
        if deleted_count > 0:
            logger.info(f"Cleanup completed: {deleted_count} files deleted")
        
        return deleted_count
        
    except Exception as e:
        logger.error(f"Cleanup failed: {str(e)}")
        return 0

def ensure_upload_directory(upload_folder: str) -> bool:
    """
    Ensure upload directory exists
    
    Args:
        upload_folder: Path to upload folder
        
    Returns:
        True if directory exists or was created successfully
    """
    try:
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder, exist_ok=True)
            logger.info(f"Created upload directory: {upload_folder}")
        
        return os.path.exists(upload_folder)
        
    except Exception as e:
        logger.error(f"Failed to create upload directory: {str(e)}")
        return False

def validate_image_file(file_path: str) -> dict:
    """
    Validate uploaded image file
    
    Args:
        file_path: Path to the uploaded file
        
    Returns:
        Dictionary with validation results
    """
    validation_result = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'file_info': {}
    }
    
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            validation_result['valid'] = False
            validation_result['errors'].append('File does not exist')
            return validation_result
        
        # Get file info
        file_size = os.path.getsize(file_path)
        file_size_mb = file_size / (1024 * 1024)
        
        validation_result['file_info'] = {
            'size_bytes': file_size,
            'size_mb': round(file_size_mb, 2),
            'extension': get_file_extension(os.path.basename(file_path))
        }
        
        # Check file size (16MB limit)
        if file_size_mb > 16:
            validation_result['valid'] = False
            validation_result['errors'].append(f'File too large: {file_size_mb:.2f}MB (max 16MB)')
        
        # Check if file is empty
        if file_size == 0:
            validation_result['valid'] = False
            validation_result['errors'].append('File is empty')
        
        # Try to open as image
        try:
            from PIL import Image
            
            with Image.open(file_path) as img:
                validation_result['file_info'].update({
                    'format': img.format,
                    'mode': img.mode,
                    'width': img.width,
                    'height': img.height
                })
                
                # Check image dimensions
                if img.width < 50 or img.height < 50:
                    validation_result['warnings'].append('Image resolution is very low')
                
                if img.width > 10000 or img.height > 10000:
                    validation_result['warnings'].append('Image resolution is very high - processing may be slow')
        
        except Exception as e:
            validation_result['valid'] = False
            validation_result['errors'].append(f'Invalid image file: {str(e)}')
    
    except Exception as e:
        validation_result['valid'] = False
        validation_result['errors'].append(f'File validation failed: {str(e)}')
    
    return validation_result

def create_safe_filename(original_filename: str, timestamp: str = None) -> str:
    """
    Create a safe filename with timestamp
    
    Args:
        original_filename: Original filename
        timestamp: Optional timestamp string
        
    Returns:
        Safe filename with timestamp
    """
    try:
        if not timestamp:
            timestamp = str(int(time.time()))
        
        # Get file extension
        if '.' in original_filename:
            name, ext = original_filename.rsplit('.', 1)
            ext = ext.lower()
        else:
            name = original_filename
            ext = ''
        
        # Clean filename (remove special characters)
        safe_name = ''.join(c for c in name if c.isalnum() or c in ('-', '_')).strip()
        
        # Ensure filename is not empty
        if not safe_name:
            safe_name = 'uploaded_image'
        
        # Create final filename
        if ext:
            return f"{timestamp}_{safe_name}.{ext}"
        else:
            return f"{timestamp}_{safe_name}"
            
    except Exception as e:
        logger.error(f"Failed to create safe filename: {str(e)}")
        return f"{int(time.time())}_image.jpg"