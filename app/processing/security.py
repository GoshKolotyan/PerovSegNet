import os
import logging

def validate_upload(uploaded_file) -> bool:
    """Validate uploaded file against security constraints"""
    from config import AppConfig
    
    if uploaded_file.size > AppConfig.get('MAX_FILE_SIZE'):
        logging.warning(f"File size exceeded: {uploaded_file.size}")
        raise ValueError("File size exceeds maximum allowed limit")
        
    if uploaded_file.type not in AppConfig.get('ALLOWED_MIME_TYPES'):
        logging.warning(f"Invalid file type: {uploaded_file.type}")
        raise ValueError("Unsupported file format")
        
    return True

def safe_save_path(user_input: str) -> str:
    """Sanitize and validate save directory path"""
    from config import AppConfig
    
    base_dir = os.path.abspath(AppConfig.get('SAVE_DIR'))
    requested_path = os.path.abspath(user_input)
    
    if not requested_path.startswith(base_dir):
        logging.error(f"Path traversal attempt detected: {user_input}")
        raise ValueError("Invalid save directory requested")
        
    os.makedirs(requested_path, exist_ok=True)
    return requested_path