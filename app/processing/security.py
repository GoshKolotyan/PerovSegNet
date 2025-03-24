import os
import cv2
import logging
from config import AppConfig
from datetime import datetime


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
def save_segmented_image(result, uploaded_file_name, percentage: float) -> str:

    save_path = AppConfig.get('SAVE_DIR')
    os.makedirs(save_path, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    safe_uploaded_filename = uploaded_file_name.replace(" ", "_").replace("/", "_")

    image_filename = f"segmented_{safe_uploaded_filename}_{timestamp}.png"
    text_filename = f"segmented_{safe_uploaded_filename}_{timestamp}.txt"

    image_save_path = os.path.join(save_path, image_filename)
    text_save_path = os.path.join(save_path, text_filename)

    result_bgr = cv2.cvtColor(result, cv2.COLOR_RGB2BGR)
    cv2.imwrite(image_save_path, result_bgr)

    with open(text_save_path, "w") as f:
        f.write(f"Percentage: {percentage:.2f}%")

    return image_save_path