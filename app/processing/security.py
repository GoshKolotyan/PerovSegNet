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

