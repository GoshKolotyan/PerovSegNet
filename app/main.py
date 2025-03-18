import streamlit as st
import logging
from ui.components import file_uploader, display_results, save_interface
from processing.image_processor import ImageProcessor
from processing.security import validate_upload
from config import AppConfig

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    st.set_page_config(page_title="Image Segmenter", layout="wide")
    st.title("Professional Image Segmentation App")
    
    uploaded_file = file_uploader()
    
    if uploaded_file:
        try:
            validate_upload(uploaded_file)
            image_path = "temp_image.png"
            with open(image_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            processor = ImageProcessor(image_path)
            
            with st.spinner("Analyzing image..."):
                # print("Uploaded file",uploaded_file.getvalue())
                result, percentage = processor()
                
            display_results(processor.original_image, result, percentage)
            save_interface(AppConfig.get('SAVE_DIR'))
            
        except Exception as e:
            st.error(f"Processing error: {str(e)}")
            logging.exception("Application error")

if __name__ == "__main__":
    main()