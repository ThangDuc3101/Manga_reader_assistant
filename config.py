"""
Configuration file for Manga Reader Application.
Centralize all hardcoded values here for easy customization.
"""

# ============================================================================
# MODEL & DETECTION SETTINGS
# ============================================================================
YOLO_MODEL_PATH = "yolov8_manga.pt"  # Path to YOLO weights
YOLO_CONFIDENCE = 0.5  # Detection confidence threshold (0-1)
YOLO_IOU = 0.5  # Intersection over Union threshold

# ============================================================================
# TEXT RECOGNITION & TRANSLATION
# ============================================================================
SOURCE_LANGUAGE = "ja"  # Japanese (source language)
TARGET_LANGUAGE = "vi"  # Vietnamese (target language)
MAX_TEXT_LENGTH = 500   # Max characters per text block (prevent API limits)

# ============================================================================
# TEXT RENDERING
# ============================================================================
FONT_SIZE = 40  # Font size in pixels
TEXT_COLOR = (255, 0, 0)  # RGB color (red)
LINE_SPACING = 40  # Pixels between lines

# Font candidates (tested in order, first match wins)
FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
    "/System/Library/Fonts/Arial.ttf",  # macOS
    "C:\\Windows\\Fonts\\arial.ttf",  # Windows
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",  # Linux alt
]

# ============================================================================
# FILE UPLOAD & OUTPUT
# ============================================================================
ALLOWED_IMAGE_FORMATS = {'.png', '.jpg', '.jpeg', '.bmp', '.webp'}
MAX_FILE_SIZE_MB = 50
OUTPUT_DIR = 'translated'  # Directory to save translated images

# ============================================================================
# TRANSLATION API SETTINGS
# ============================================================================
# NOTE: googletrans is unofficial and may be blocked by Google
# For production, use Google Cloud Translation API instead

TRANSLATION_API_TIMEOUT = 30  # seconds
TRANSLATION_MAX_RETRIES = 3  # retry failed translations

# Google Cloud Translation (optional, more stable)
# Requires: pip install google-cloud-translate
# Set GOOGLE_APPLICATION_CREDENTIALS environment variable
USE_GOOGLE_CLOUD_API = False  # Set True to use Cloud API instead of googletrans
GOOGLE_CLOUD_PROJECT_ID = None  # Required if USE_GOOGLE_CLOUD_API=True

# ============================================================================
# STREAMLIT UI SETTINGS
# ============================================================================
PAGE_TITLE = "MANGA READER"
PAGE_ICON = "📖"
LAYOUT = "wide"  # or "centered"
INITIAL_SIDEBAR_STATE = "expanded"  # or "collapsed"

# ============================================================================
# LOGGING
# ============================================================================
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = "manga_reader.log"  # None to disable file logging

# ============================================================================
# PERFORMANCE TUNING
# ============================================================================
CACHE_MODELS = True  # Use Streamlit cache for models
BATCH_TRANSLATION = True  # Group text before translating (faster)
BATCH_SIZE = 10  # Number of texts to translate per API call

# ============================================================================
# FEATURE FLAGS
# ============================================================================
ENABLE_LANGUAGE_SELECTION = False  # Let users choose target language
ENABLE_BATCH_FOLDER = False  # Support uploading folders
ENABLE_MODEL_SELECTION = False  # Let users choose YOLO model
ENABLE_EXPORT_PDF = False  # Export results as PDF

# ============================================================================
# DEVELOPMENT
# ============================================================================
DEBUG_MODE = False  # Show debug info, don't cache models
SAVE_INTERMEDIATES = False  # Save detection masks, crops, etc. for debugging
PROFILE_PERFORMANCE = False  # Measure execution time for each step
