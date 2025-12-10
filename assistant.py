import streamlit as st
from PIL import Image
from reader import Manga_Reader
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Allowed image formats
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp', '.webp'}
MAX_FILE_SIZE_MB = 50
OUTPUT_DIR = 'translated'


@st.cache_resource
def load_manga_reader():
    """
    Load and cache the Manga Reader model to avoid reloading on every run.
    
    Returns:
        Manga_Reader: Cached instance of the manga reader.
    """
    try:
        logger.info("Loading Manga Reader model...")
        reader = Manga_Reader()
        logger.info("Manga Reader model loaded successfully")
        return reader
    except Exception as e:
        logger.error(f"Failed to load Manga Reader: {e}")
        st.error(f"Failed to load model: {e}")
        raise


def validate_uploaded_file(uploaded_file):
    """
    Validate uploaded file for correct format and size.
    
    Parameters:
        uploaded_file: Streamlit uploaded file object.
        
    Returns:
        tuple: (is_valid: bool, error_message: str)
    """
    if uploaded_file is None:
        return False, "No file provided"
    
    # Check file extension
    file_ext = Path(uploaded_file.name).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        return False, f"Invalid file format. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
    
    # Check file size (Streamlit already limits, but good practice)
    file_size_mb = uploaded_file.size / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        return False, f"File too large. Max size: {MAX_FILE_SIZE_MB}MB, got {file_size_mb:.1f}MB"
    
    return True, ""


def ensure_output_directory():
    """Create output directory if it doesn't exist."""
    try:
        Path(OUTPUT_DIR).mkdir(exist_ok=True)
        logger.info(f"Output directory ensured: {OUTPUT_DIR}")
    except Exception as e:
        logger.error(f"Failed to create output directory: {e}")
        raise


def process_image(reader, uploaded_file):
    """
    Process a single image: translate text and save result.
    
    Parameters:
        reader (Manga_Reader): The manga reader instance.
        uploaded_file: Streamlit uploaded file object.
        
    Returns:
        tuple: (processed_image: PIL.Image or None, success: bool, message: str)
    """
    try:
        # Validate file
        is_valid, error_msg = validate_uploaded_file(uploaded_file)
        if not is_valid:
            return None, False, error_msg
        
        # Open and process image
        logger.info(f"Processing image: {uploaded_file.name}")
        image = Image.open(uploaded_file)
        
        # Verify image is valid
        if image.size[0] <= 0 or image.size[1] <= 0:
            return None, False, "Invalid image dimensions"
        
        # Process with manga reader
        processed_image = reader(image)
        
        if processed_image is None:
            return None, False, "Failed to process image"
        
        # Save result
        ensure_output_directory()
        image_name = Path(uploaded_file.name).stem + '.png'
        output_path = Path(OUTPUT_DIR) / image_name
        
        processed_image.save(str(output_path))
        logger.info(f"Image saved to: {output_path}")
        
        return processed_image, True, f"Successfully saved to {output_path}"
        
    except Exception as e:
        logger.error(f"Error processing image {uploaded_file.name}: {e}")
        return None, False, f"Error: {str(e)}"


def app():
    """
    Main entry point for the MANGA READER application.
    
    Features:
    - Upload multiple manga images
    - Automatically translate Japanese text to Vietnamese
    - Display results
    - Save translated images
    """
    st.title("MANGA READER")
    st.text("Author: ThangBui")
    st.text("Framework: Ultralytics, OCR, Streamlit")
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Load cached reader
    try:
        reader = load_manga_reader()
    except Exception as e:
        st.error("Failed to initialize manga reader. Please check your model file.")
        return
    
    # File uploader
    uploaded_images = st.sidebar.file_uploader(
        "Upload manga images (JPG, PNG, etc.)",
        accept_multiple_files=True,
        type=['png', 'jpg', 'jpeg', 'bmp', 'webp']
    )
    
    if not uploaded_images:
        st.info("👆 Upload manga images from the sidebar to get started!")
        return
    
    # Process each image
    progress_bar = st.progress(0)
    for idx, uploaded_image in enumerate(uploaded_images):
        st.subheader(f"Processing: {uploaded_image.name}")
        
        # Process image
        processed_img, success, message = process_image(reader, uploaded_image)
        
        if success:
            st.success(message)
            st.balloons()
            st.image(processed_img, caption=f"Translated: {uploaded_image.name}")
        else:
            st.error(message)
        
        # Update progress
        progress_bar.progress((idx + 1) / len(uploaded_images))
    
    st.success("All images processed!") 