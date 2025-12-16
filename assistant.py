import streamlit as st
from PIL import Image
from reader import Manga_Reader
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tạo thư mục translated nếu chưa tồn tại
TRANSLATED_DIR = "translated"
os.makedirs(TRANSLATED_DIR, exist_ok=True)

@st.cache_resource
def load_reader():
    """
    Load Manga Reader model once and cache it.
    This prevents reloading the heavy models on each interaction.
    """
    try:
        logger.info("Loading Manga Reader model...")
        reader = Manga_Reader()
        logger.info("Manga Reader loaded successfully")
        return reader
    except Exception as e:
        logger.error(f"Error loading Manga Reader: {e}")
        st.error(f"Failed to load Manga Reader: {str(e)}")
        raise

def app():
    """
    Main entry point of the MANGA READER application. 
    
    Features:
    - Upload multiple manga images
    - Process with detection, OCR, translation
    - Display translated result
    - Save to translated folder
    """
    
    st.title("MANGA READER")
    st.text("Author: ThangBui")
    st.text("Framework: Ultralytics, OCR, Streamlit")
    
    try:
        # Load reader model (cached)
        reader = load_reader()
    except Exception as e:
        st.error(f"Cannot initialize Manga Reader: {str(e)}")
        logger.error(f"Failed to initialize reader: {e}")
        return
    
    # File uploader
    try:
        upload_images = st.sidebar.file_uploader(
            "Upload multiple files",
            accept_multiple_files=True,
            type=['jpg', 'jpeg', 'png']
        )
    except Exception as e:
        st.error(f"Error in file upload: {str(e)}")
        logger.error(f"File upload error: {e}")
        return
    
    if not upload_images:
        st.info("Please upload manga images to start translation")
        return
    
    # Process each uploaded image
    for upload_image in upload_images:
        st.divider()
        st.subheader(f"Processing: {upload_image.name}")
        
        try:
            # Open image
            try:
                image = Image.open(upload_image)
                logger.info(f"Opened image: {upload_image.name}")
            except Exception as e:
                st.error(f"Cannot open image {upload_image.name}: {str(e)}")
                logger.error(f"Image open error for {upload_image.name}: {e}")
                continue
            
            # Process image with error handling
            try:
                with st.spinner("🔍 Detecting textboxes..."):
                    imageTrans = reader(image)
                logger.info(f"Successfully processed: {upload_image.name}")
            except Exception as e:
                st.error(f"Error processing image {upload_image.name}: {str(e)}")
                logger.error(f"Processing error for {upload_image.name}: {e}")
                continue
            
            # Display result
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Original**")
                st.image(image, use_column_width=True)
            with col2:
                st.write("**Translated**")
                st.image(imageTrans, use_column_width=True)
            
            st.balloons()
            
            # Save translated image
            try:
                image_name = upload_image.name.split('.')[0] + '.png'
                save_path = os.path.join(TRANSLATED_DIR, image_name)
                imageTrans.save(save_path)
                st.success(f"✅ Saved to `translated/{image_name}`")
                logger.info(f"Image saved: {save_path}")
            except Exception as e:
                st.warning(f"Cannot save image: {str(e)}")
                logger.error(f"Error saving image {upload_image.name}: {e}")
        
        except Exception as e:
            st.error(f"Unexpected error processing {upload_image.name}: {str(e)}")
            logger.error(f"Unexpected error for {upload_image.name}: {e}")
            continue
