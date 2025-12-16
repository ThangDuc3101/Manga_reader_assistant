import streamlit as st
from PIL import Image
from reader import Manga_Reader, SUPPORTED_LANGUAGES
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tạo thư mục translated nếu chưa tồn tại
TRANSLATED_DIR = "translated"
os.makedirs(TRANSLATED_DIR, exist_ok=True)

@st.cache_resource
def load_reader(language='vi'):
    """
    Load Manga Reader model once and cache it.
    This prevents reloading the heavy models on each interaction.
    """
    try:
        logger.info(f"Loading Manga Reader model for language: {language}...")
        reader = Manga_Reader(target_language=language)
        logger.info("Manga Reader loaded successfully")
        return reader
    except Exception as e:
        logger.error(f"Error loading Manga Reader: {e}")
        st.error(f"Failed to load Manga Reader: {str(e)}")
        raise
    
@st.cache_resource
def get_language_options():
    """Get supported language options."""
    return {f"{code} - {name}": code for code, name in SUPPORTED_LANGUAGES.items()}

def app():
    """
    Main entry point of the MANGA READER application. 
    
    Features:
    - Upload multiple manga images
    - Process with detection, OCR, translation
    - Display translated result
    - Save to translated folder
    - Multi-language support
    - Processing statistics
    """
    
    st.title("MANGA READER")
    st.text("Author: ThangBui")
    st.text("Framework: Ultralytics, OCR, Streamlit")
    
    # Sidebar settings
    st.sidebar.markdown("### ⚙️ Settings")
    
    language_options = get_language_options()
    selected_language_display = st.sidebar.selectbox(
        "🌐 Select Target Language",
        options=list(language_options.keys()),
        index=0  # Default to Vietnamese
    )
    selected_language_code = language_options[selected_language_display]
    
    try:
        # Load reader model (cached) with selected language
        reader = load_reader(selected_language_code)
    except Exception as e:
        st.error(f"Cannot initialize Manga Reader: {str(e)}")
        logger.error(f"Failed to initialize reader: {e}")
        return
    
    # File uploader
    st.sidebar.markdown("### 📤 Upload")
    try:
        upload_images = st.sidebar.file_uploader(
            "Upload manga images",
            accept_multiple_files=True,
            type=['jpg', 'jpeg', 'png']
        )
    except Exception as e:
        st.error(f"Error in file upload: {str(e)}")
        logger.error(f"File upload error: {e}")
        return
    
    if not upload_images:
        st.info("📚 Please upload manga images to start translation")
        
        # Show example supported languages
        st.sidebar.markdown("### 📖 Supported Languages")
        lang_cols = st.sidebar.columns(2)
        for i, (code, name) in enumerate(list(SUPPORTED_LANGUAGES.items())[:6]):
            with lang_cols[i % 2]:
                st.caption(f"• {name}")
        return
    
    # Statistics tracking
    stats_placeholder = st.sidebar.empty()
    
    # Process each uploaded image
    total_images = len(upload_images)
    progress_bar = st.progress(0)
    
    for idx, upload_image in enumerate(upload_images):
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
                with st.spinner(f"🔍 Processing... {idx+1}/{total_images}"):
                    imageTrans = reader(image)
                logger.info(f"Successfully processed: {upload_image.name}")
            except Exception as e:
                st.error(f"Error processing image {upload_image.name}: {str(e)}")
                logger.error(f"Processing error for {upload_image.name}: {e}")
                continue
            
            # Display result
            col1, col2 = st.columns(2)
            with col1:
                st.write("**📖 Original**")
                st.image(image, use_column_width=True)
            with col2:
                st.write(f"**✅ Translated ({selected_language_display.split('-')[0]})**")
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
        
        finally:
            # Update progress
            progress_bar.progress((idx + 1) / total_images)
    
    # Show statistics
    stats = reader.get_stats()
    if stats['processed_images'] > 0:
        st.sidebar.markdown("### 📊 Statistics")
        st.sidebar.metric("Images Processed", stats['processed_images'])
        st.sidebar.metric("Total Textboxes", stats['total_textboxes'])
        st.sidebar.metric("Total Time", f"{stats['total_time']:.2f}s")
        if stats['total_textboxes'] > 0:
            avg_per_image = stats['total_time'] / stats['processed_images']
            st.sidebar.metric("Avg Time/Image", f"{avg_per_image:.2f}s")
