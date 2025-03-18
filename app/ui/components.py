import streamlit as st
import numpy as np
from typing import Optional

def file_uploader() -> Optional[bytes]:
    """Secure file upload component"""
    return st.file_uploader(
        "Choose an image file",
        type=["png", "jpg", "jpeg"],
        help="Maximum file size: 10MB"
    )

def display_results(original: np.ndarray, result: np.ndarray, percentage: float):
    """Display results with metrics"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Original Image")
        st.image(original)
        
    with col2:
        st.subheader(f"Segmented Overlay ({percentage:.2f}%)")
        st.image(result)
        