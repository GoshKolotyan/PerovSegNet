import streamlit as st
import numpy as np
from typing import Optional, Tuple
from PIL import Image
import io

def apply_custom_css():
    """Apply minimal custom CSS"""
    st.markdown("""
        <style>
        .stApp {
            max-width: 1400px;
            margin: 0 auto;
        }
        </style>
    """, unsafe_allow_html=True)

def render_header():
    """Render simple app header"""
    st.title("PerovSegNet - Material Segmentation")

def file_uploader() -> Tuple[Optional[bytes], str]:
    """File upload component with material selection"""
    col1, col2 = st.columns([2, 1])

    with col1:
        uploaded_file = st.file_uploader(
            "Choose an image file",
            type=["png", "jpg", "jpeg"],
            help="Supported formats: PNG, JPG, JPEG (Max: 10MB)"
        )

    with col2:
        material_selection = st.selectbox(
            "Material Detection Mode",
            options=["auto", "bright", "dark"],
            index=0,
            help="""
            Auto: Automatically detect material (recommended)
            Bright: Material is brighter than background
            Dark: Material is darker than background
            """
        )

    return uploaded_file, material_selection

def display_results(original: np.ndarray, result: np.ndarray, percentage: float):
    """Display results in simple layout"""
    st.divider()

    # Display metric
    st.metric(label="Material Coverage", value=f"{100-percentage:.2f}%")

    st.divider()

    # Display images side by side
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Original Image")
        st.image(original, use_container_width=True)

    with col2:
        st.subheader("Segmented Material")
        st.image(result, use_container_width=True)

def create_download_button(result: np.ndarray, filename: str, percentage: float):
    """Create download button for segmented image"""
    result_pil = Image.fromarray(result.astype('uint8'))

    buf = io.BytesIO()
    result_pil.save(buf, format='PNG')
    byte_im = buf.getvalue()

    st.download_button(
        label="Download Segmented Image",
        data=byte_im,
        file_name=f"{filename.split('.')[0]}_segmented_{percentage:.1f}pct.png",
        mime="image/png"
    )
