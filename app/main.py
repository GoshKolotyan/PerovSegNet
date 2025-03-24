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
from ui.components import file_uploader, display_results

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
    st.set_page_config(page_title="Image Segmenter", layout="wide")
    st.title("Image Segmentation App")

    uploaded_file = file_uploader()
    temp_path = None

    if uploaded_file:
        try:
            validate_upload(uploaded_file)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                temp_file.write(uploaded_file.getbuffer())
                temp_path = temp_file.name

            processor = ImageProcessor(temp_path)

            with st.spinner("Analyzing image..."):
                result, percentage = processor()

            display_results(processor.original_image, result, percentage)

            save_file = save_segmented_image(result, uploaded_file.name)

            st.success(f"Image successfully saved at {save_file}")
            logger.info(f"Image processed and saved: {save_file}")

        except Exception as e:
            st.error(f"Processing error: {str(e)}")
            logger.exception("Application error")
        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
                logger.info(f"Temporary file deleted: {temp_path}")


if __name__ == "__main__":
    main()