import os
import cv2
import logging
from logging.handlers import RotatingFileHandler
import tempfile
import streamlit as st

from datetime import datetime
from config import AppConfig
from processing.security import validate_upload, save_segmented_image
from processing.image_processor import ImageProcessor
from ui.components import (
    apply_custom_css,
    render_header,
    file_uploader,
    display_results,
    create_download_button
)

# Setup logging
logs_dir = AppConfig.DEFAULTS.get('LOGS_DIR', './app/logs')
os.makedirs(logs_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(
            os.path.join(logs_dir, 'app.log'), maxBytes=5 * 1024 * 1024, backupCount=3
        ),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def main():
    # Configure page
    st.set_page_config(
        page_title="PerovSegNet - Material Segmentation",
        layout="wide"
    )

    # Apply custom styling
    apply_custom_css()

    # Render header
    render_header()

    # File upload and material selection
    uploaded_file, material_selection = file_uploader()
    temp_path = None

    if uploaded_file:
        try:
            # Validate upload
            validate_upload(uploaded_file)

            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                temp_file.write(uploaded_file.getbuffer())
                temp_path = temp_file.name

            # Process image with selected material detection mode
            processor = ImageProcessor(temp_path, material_selection=material_selection)

            # Show progress
            with st.spinner("Analyzing image..."):
                result, percentage = processor()

            # Display results
            display_results(processor.original_image, result, percentage)

            # Save segmented image
            save_file = save_segmented_image(result, uploaded_file.name, percentage)

            # Download button
            create_download_button(result, uploaded_file.name, percentage)

            # Success message
            st.success(f"Image successfully processed and saved at {save_file}")
            logger.info(f"Image processed: {save_file}, Material: {percentage:.2f}%, Mode: {material_selection}")

        except Exception as e:
            st.error(f"Processing error: {str(e)}")
            logger.exception("Application error")
        finally:
            # Cleanup temporary file
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
                logger.info(f"Temporary file deleted: {temp_path}")


if __name__ == "__main__":
    main()