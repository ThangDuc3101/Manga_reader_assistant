import streamlit as st
from PIL import Image
from reader import Manga_Reader
import os
import logging
from pathlib import Path
from datetime import datetime
import time

logger = logging.getLogger(__name__)

# Allowed image formats
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp', '.webp'}
MAX_FILE_SIZE_MB = 50
OUTPUT_DIR = 'translated'

# Session state initialization
if 'processing_history' not in st.session_state:
    st.session_state.processing_history = []
if 'failed_files' not in st.session_state:
    st.session_state.failed_files = {}


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


def process_image(reader, uploaded_file, status_container=None):
    """
    Process a single image: translate text and save result with detailed status.
    
    Parameters:
        reader (Manga_Reader): The manga reader instance.
        uploaded_file: Streamlit uploaded file object.
        status_container: Optional Streamlit container for status updates.
        
    Returns:
        tuple: (processed_image: PIL.Image or None, original_image: PIL.Image or None, 
                success: bool, message: str)
    """
    original_image = None
    try:
        # Step 1: Validate file
        if status_container:
            status_container.update(label="Validating file...", state="running")
        
        is_valid, error_msg = validate_uploaded_file(uploaded_file)
        if not is_valid:
            logger.warning(f"Validation failed for {uploaded_file.name}: {error_msg}")
            return None, None, False, error_msg
        
        # Step 2: Open image
        if status_container:
            status_container.update(label="Loading image...", state="running")
        
        logger.info(f"Processing image: {uploaded_file.name}")
        image = Image.open(uploaded_file)
        original_image = image.copy()
        
        # Verify image is valid
        if image.size[0] <= 0 or image.size[1] <= 0:
            return None, original_image, False, "Invalid image dimensions"
        
        # Step 3: Process with manga reader
        if status_container:
            status_container.update(label="Translating text (OCR + Translation)...", state="running")
        
        start_time = time.time()
        processed_image = reader(image)
        process_time = time.time() - start_time
        
        if processed_image is None:
            return None, original_image, False, "Failed to process image"
        
        # Step 4: Save result
        if status_container:
            status_container.update(label="Saving result...", state="running")
        
        ensure_output_directory()
        image_name = Path(uploaded_file.name).stem + '.png'
        output_path = Path(OUTPUT_DIR) / image_name
        
        processed_image.save(str(output_path))
        logger.info(f"Image saved to: {output_path} (Processing time: {process_time:.2f}s)")
        
        # Mark as completed
        if status_container:
            status_container.update(label="✓ Complete", state="complete")
        
        return processed_image, original_image, True, f"Processed in {process_time:.2f}s"
        
    except Exception as e:
        logger.error(f"Error processing image {uploaded_file.name}: {e}", exc_info=True)
        if status_container:
            status_container.update(label="✗ Failed", state="error")
        return None, original_image, False, f"Error: {str(e)}"


def display_before_after(original_img, processed_img, file_name, col1, col2):
    """Display before/after comparison of manga images."""
    with col1:
        st.image(original_img, caption="Original", use_column_width=True)
    with col2:
        st.image(processed_img, caption="Translated", use_column_width=True)


def retry_processing(reader, uploaded_file):
    """Allow user to retry failed image processing."""
    st.warning(f"⚠️ Processing failed for {uploaded_file.name}. Let's try again.")
    
    if st.button(f"🔄 Retry {uploaded_file.name}", key=f"retry_{uploaded_file.name}"):
        st.session_state.failed_files[uploaded_file.name] = False
        st.rerun()


def app():
    """
    Main entry point for the MANGA READER application.
    
    Features:
    - Upload multiple manga images
    - Automatically translate Japanese text to Vietnamese
    - Display results with real-time progress
    - Show before/after comparison
    - Error recovery with retry functionality
    - Processing history and performance metrics
    """
    # Page configuration
    st.set_page_config(page_title="Manga Reader", layout="wide", initial_sidebar_state="expanded")
    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("📖 MANGA READER")
    with col2:
        st.caption("v2.0 - Enhanced UI/UX")
    
    st.text("Author: ThangBui | Framework: Ultralytics, OCR, Streamlit")
    st.divider()
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        show_before_after = st.checkbox("Show Before/After Preview", value=True)
        st.divider()
        
        if st.session_state.processing_history:
            st.subheader("📊 Processing History")
            for record in st.session_state.processing_history[-5:]:  # Show last 5
                col_time, col_status = st.columns([2, 1])
                with col_time:
                    st.caption(record['file'])
                with col_status:
                    status_emoji = "✓" if record['success'] else "✗"
                    st.caption(f"{status_emoji} {record['time']:.2f}s")
    
    # Load cached reader with loading indicator
    reader = None
    try:
        with st.spinner("🤖 Loading Manga Reader model..."):
            reader = load_manga_reader()
        st.success("✓ Model loaded successfully")
    except Exception as e:
        st.error("❌ Failed to initialize manga reader. Please check your model file.")
        logger.error(f"Model loading failed: {e}")
        return
    
    st.divider()
    
    # File uploader
    st.header("📤 Upload Images")
    uploaded_images = st.file_uploader(
        "Select manga images (JPG, PNG, etc.)",
        accept_multiple_files=True,
        type=['png', 'jpg', 'jpeg', 'bmp', 'webp']
    )
    
    if not uploaded_images:
        st.info("👆 Upload manga images to get started!")
        st.markdown("""
        **Supported formats:** PNG, JPG, JPEG, BMP, WebP (Max 50MB each)
        
        **What it does:**
        1. Detects text in manga images
        2. Translates Japanese → Vietnamese
        3. Overlays translated text on images
        """)
        return
    
    st.divider()
    st.header("🔄 Processing Progress")
    
    # Overall progress tracking
    total_images = len(uploaded_images)
    successful = 0
    failed = 0
    skipped = 0
    
    # Progress bar and metrics
    col1, col2, col3, col4 = st.columns(4)
    progress_placeholder = st.empty()
    metrics_placeholder = st.empty()
    
    # Process each image
    results_container = st.container()
    
    for idx, uploaded_image in enumerate(uploaded_images):
        # Update overall progress
        current_progress = (idx + 1) / total_images
        
        with progress_placeholder.container():
            st.progress(current_progress, text=f"Processing {idx + 1}/{total_images}")
        
        # Create expandable section for each image
        with results_container.expander(
            f"📄 {uploaded_image.name}", 
            expanded=(idx == 0)  # First image expanded by default
        ):
            # Status container with detailed processing steps
            with st.status("Processing...", expanded=True) as status:
                # Process image
                start_time = time.time()
                processed_img, original_img, success, message = process_image(
                    reader, uploaded_image, status_container=status
                )
                elapsed_time = time.time() - start_time
                
                # Record in history
                st.session_state.processing_history.append({
                    'file': uploaded_image.name,
                    'success': success,
                    'time': elapsed_time,
                    'timestamp': datetime.now()
                })
                
                # Update metrics
                if success:
                    successful += 1
                    status.update(label="✓ Completed successfully!", state="complete")
                else:
                    failed += 1
                    status.update(label="✗ Processing failed", state="error")
            
            # Display results
            if success:
                # Show success message with timing
                st.success(f"✓ {message}", icon="✓")
                
                # Before/after preview
                if show_before_after and original_img and processed_img:
                    st.markdown("**Before & After Comparison:**")
                    col1, col2 = st.columns(2)
                    display_before_after(original_img, processed_img, uploaded_image.name, col1, col2)
                else:
                    # Just show processed image
                    st.image(processed_img, caption=f"Translated: {uploaded_image.name}", use_column_width=True)
                
                # Download button
                if processed_img:
                    img_path = Path(OUTPUT_DIR) / (Path(uploaded_image.name).stem + '.png')
                    if img_path.exists():
                        with open(img_path, 'rb') as f:
                            st.download_button(
                                label="⬇️ Download Translated Image",
                                data=f.read(),
                                file_name=img_path.name,
                                mime="image/png"
                            )
                
                st.balloons()
            else:
                # Error handling
                st.error(f"❌ {message}", icon="✗")
                
                # Retry option
                if st.button("🔄 Retry", key=f"retry_{uploaded_image.name}_{idx}"):
                    # Clear from failed_files and rerun
                    if uploaded_image.name in st.session_state.failed_files:
                        del st.session_state.failed_files[uploaded_image.name]
                    st.rerun()
                
                # Show original for reference
                if original_img:
                    st.image(original_img, caption="Original Image (for reference)", width=300)
    
    # Final summary
    st.divider()
    st.header("📈 Summary")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Successful", successful, f"{(successful/total_images)*100:.0f}%")
    with col2:
        st.metric("Failed", failed, f"{(failed/total_images)*100:.0f}%" if failed > 0 else "0%")
    with col3:
        avg_time = sum([r['time'] for r in st.session_state.processing_history[-total_images:]])/total_images
        st.metric("Avg Time", f"{avg_time:.2f}s", "per image")
    
    if successful == total_images:
        st.success(f"🎉 All {total_images} images processed successfully!")
    elif successful > 0:
        st.warning(f"⚠️ {successful}/{total_images} images processed. {failed} failed.")


if __name__ == "__main__":
    app() 