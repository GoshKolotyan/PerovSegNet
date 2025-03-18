import streamlit as st
import numpy as np
from typing import Optional
from processing.security import safe_save_path

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
        st.image(original, use_column_width=True)
        
    with col2:
        st.subheader(f"Segmented Overlay ({percentage:.2f}%)")
        st.image(result, use_column_width=True)
        
    st.progress(min(percentage/100, 1.0))

def save_interface(default_dir: str):
    """Safe save component"""
    user_input = st.text_input("Save directory:", default_dir)
    if st.button("Save Result"):
        try:
            save_path = safe_save_path(user_input)
            st.success(f"Results will be saved to: {save_path}")
        except ValueError as e:
            st.error(str(e))