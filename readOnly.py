import streamlit as st
from PIL import Image
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def load_and_display_image(uploaded_file):
    """
    Load and display an image with error handling.
    
    Parameters:
        uploaded_file: Streamlit uploaded file object.
        
    Returns:
        tuple: (image: PIL.Image or None, success: bool, error_message: str)
    """
    try:
        if uploaded_file is None:
            return None, False, "No file provided"
        
        # Try to open image
        image = Image.open(uploaded_file)
        
        # Validate image
        if image.size[0] <= 0 or image.size[1] <= 0:
            return None, False, "Invalid image dimensions"
        
        logger.info(f"Loaded image: {uploaded_file.name} ({image.size})")
        return image, True, ""
        
    except Image.UnidentifiedImageError:
        error_msg = f"Invalid image file: {uploaded_file.name}"
        logger.error(error_msg)
        return None, False, error_msg
    except Exception as e:
        error_msg = f"Error loading {uploaded_file.name}: {str(e)}"
        logger.error(error_msg)
        return None, False, error_msg


def app():
    """
    Display translated manga images from uploaded files.
    
    Features:
    - Upload translated manga images
    - View all uploaded images
    - Error handling for corrupted files
    """
    st.title("MANGA READER")
    st.text("Author: ThangBui")
    st.text("Framework: Ultralytics, OCR, Streamlit")
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    st.write("📖 In this tab, you can view translated manga that you previously saved")
    
    # File uploader
    uploaded_images = st.sidebar.file_uploader(
        "Upload translated manga images",
        accept_multiple_files=True,
        type=['png', 'jpg', 'jpeg', 'bmp', 'webp']
    )
    
    if not uploaded_images:
        st.info("👆 Upload translated manga images from the sidebar to view them!")
        return
    
    # Display images
    st.subheader(f"Total images: {len(uploaded_images)}")
    
    for idx, uploaded_image in enumerate(uploaded_images, 1):
        try:
            image, success, error_msg = load_and_display_image(uploaded_image)
            
            if success:
                # Display with details
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.image(image, caption=f"{uploaded_image.name}", use_column_width=True)
                with col2:
                    st.text(f"Size: {image.size[0]}x{image.size[1]}")
            else:
                st.error(f"Image {idx}: {error_msg}")
                
        except Exception as e:
            logger.error(f"Unexpected error with image {idx}: {e}")
            st.error(f"Unexpected error loading image {idx}: {str(e)}")