import streamlit as st
from PIL import Image
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TRANSLATED_DIR = "translated"

def app():
    """
    Display translated manga images from the 'translated' folder.
    
    Features:
    - Browse translated images from local folder
    - Upload and view translated images
    - Display with viewer
    """
    
    st.title("MANGA READER")
    st.text("Author: ThangBui")
    st.text("Framework: Ultralytics, OCR, Streamlit")
    
    st.write("In this tab, you can read translated manga")
    
    # Create two columns for different viewing options
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📤 Upload Translated Images")
        try:
            upload_images = st.file_uploader(
                "Upload translated images",
                accept_multiple_files=True,
                type=['jpg', 'jpeg', 'png']
            )
            
            if upload_images:
                for upload_image in upload_images:
                    try:
                        image = Image.open(upload_image)
                        st.image(image, caption=upload_image.name, use_column_width=True)
                        logger.info(f"Displayed uploaded image: {upload_image.name}")
                    except Exception as e:
                        st.error(f"Cannot open image {upload_image.name}: {str(e)}")
                        logger.error(f"Error opening image {upload_image.name}: {e}")
        except Exception as e:
            st.error(f"Error in file upload: {str(e)}")
            logger.error(f"File upload error: {e}")
    
    with col2:
        st.subheader("📁 Saved Translations")
        try:
            if os.path.exists(TRANSLATED_DIR):
                translated_files = [f for f in os.listdir(TRANSLATED_DIR) 
                                   if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                
                if translated_files:
                    st.info(f"Found {len(translated_files)} translated images")
                    
                    for filename in sorted(translated_files):
                        try:
                            filepath = os.path.join(TRANSLATED_DIR, filename)
                            image = Image.open(filepath)
                            st.image(image, caption=filename, use_column_width=True)
                            logger.info(f"Displayed saved image: {filename}")
                        except Exception as e:
                            st.error(f"Cannot open {filename}: {str(e)}")
                            logger.error(f"Error opening {filename}: {e}")
                else:
                    st.info("No translated images found in the 'translated' folder yet. "
                           "Process some manga in the Assistant tab first!")
            else:
                st.warning(f"Directory '{TRANSLATED_DIR}' not found. "
                          "Process manga in the Assistant tab first!")
                logger.warning(f"Directory {TRANSLATED_DIR} not found")
        except Exception as e:
            st.error(f"Error reading translated folder: {str(e)}")
            logger.error(f"Error reading translated folder: {e}")
