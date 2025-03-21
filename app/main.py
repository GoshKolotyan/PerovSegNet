import os
import cv2
import logging
import streamlit as st

from datetime import datetime
from config import AppConfig
from processing.security import validate_upload
from processing.image_processor import ImageProcessor
from ui.components import file_uploader, display_results



logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    st.set_page_config(page_title="Image Segmenter", layout="wide")
    st.title("Image Segmentation App")
    
    uploaded_file = file_uploader()
    
    if uploaded_file:
        try:
            validate_upload(uploaded_file)
            image_path = "temp_image.png"
            with open(image_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            processor = ImageProcessor(image_path)
            
            with st.spinner("Analyzing image..."):
                result, percentage = processor()
                
            display_results(processor.original_image, result, percentage)
            save_path = AppConfig.get('SAVE_DIR')
            now = datetime.now()

            save_file = os.path.join(save_path, f"segmented_{uploaded_file.name}_{now.strftime("%Y-%m-%d %H:%M:%S")}.png")

            # Convert from RGB to BGR before saving, if needed
            result_bgr = cv2.cvtColor(result, cv2.COLOR_RGB2BGR)
            
            cv2.imwrite(save_file, result_bgr)
            
            st.success(f"Image successfully saved at {save_file}")
        except Exception as e:
            st.error(f"Processing error: {str(e)}")
            logging.exception("Application error")

if __name__ == "__main__":
    main()