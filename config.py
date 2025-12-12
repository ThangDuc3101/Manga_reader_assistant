"""
Configuration file for Manga Reader Application.
Centralize all hardcoded values here for easy customization.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file (if it exists)
load_dotenv()

# ============================================================================
# MODEL & DETECTION SETTINGS
# ============================================================================
# Primary: Roboflow Manga Bubble Detector (recommended)
USE_ROBOFLOW = True  # Use Roboflow API for model loading
ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY")  # Get from .env or environment
ROBOFLOW_MODEL = os.getenv("ROBOFLOW_MODEL", "manga-bubble-detect")  # Model name
ROBOFLOW_VERSION = int(os.getenv("ROBOFLOW_VERSION", "1"))  # Model version

# Fallback: Local YOLOv8s model (used if Roboflow unavailable)
FALLBACK_MODEL_PATH = "yolov8s.pt"  # Auto-downloads from Ultralytics
MODEL_CACHE_DIR = ".models"  # Cache directory for downloaded models
OFFLINE_MODE = False  # Set True to use cached weights without API

# Detection parameters
YOLO_CONFIDENCE = 0.5  # Detection confidence threshold (0-1)
YOLO_IOU = 0.5  # Intersection over Union threshold
ROBOFLOW_TIMEOUT = 30  # API request timeout in seconds

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
# TRANSLATION API - STABLE & PRODUCTION-READY (Phase 2, Task 3)
# ============================================================================

# Primary API: Google Cloud Translation (recommended for production)
USE_GOOGLE_CLOUD_API = os.getenv("USE_GOOGLE_CLOUD_API", "false").lower() == "true"
GOOGLE_CLOUD_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
GOOGLE_CLOUD_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Fallback: googletrans (works when Cloud API unavailable)
USE_GOOGLETRANS_FALLBACK = True  # Always keep as backup

# Retry configuration (exponential backoff)
TRANSLATION_MAX_RETRIES = int(os.getenv("TRANSLATION_MAX_RETRIES", "3"))
TRANSLATION_RETRY_BACKOFF = float(os.getenv("TRANSLATION_RETRY_BACKOFF", "1.0"))

# Cache configuration (file-based, persistent)
ENABLE_TRANSLATION_CACHE = os.getenv("ENABLE_TRANSLATION_CACHE", "true").lower() == "true"
CACHE_FILE_PATH = ".translation_cache.json"  # Git-ignored, local cache
CACHE_SIZE_LIMIT = int(os.getenv("CACHE_SIZE_LIMIT", "10000"))

# Timeout settings
TRANSLATION_API_TIMEOUT = int(os.getenv("TRANSLATION_API_TIMEOUT", "30"))

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

# ============================================================================
# PERFORMANCE OPTIMIZATION (Task 2.4)
# ============================================================================

# Image Preprocessing
USE_OPENCV = False  # True = faster preprocessing (if cv2 available)
MAX_IMAGE_WIDTH = 0  # Max width before resize (0 = no limit)
MAX_IMAGE_HEIGHT = 0  # Max height before resize (0 = no limit)
PRESERVE_ASPECT_RATIO = True  # Maintain aspect ratio when resizing

# Model Selection & Caching
YOLO_MODEL = "yolov8s.pt"  # Options: yolov8n (fast), yolov8s (balanced), yolov8m (accurate)
ENABLE_MODEL_CACHE = True  # Cache model in memory between images
MODEL_CACHE_TIMEOUT = 300  # Cache timeout in seconds

# Translation & Batch Processing
ADAPTIVE_BATCH_SIZE = True  # Adjust batch size based on text count
MAX_BATCH_SIZE = 30  # Maximum texts per API call (higher = faster)

# GPU Support
USE_GPU = False  # Enable GPU acceleration (requires CUDA/PyTorch)
GPU_DEVICE_ID = 0  # Which GPU to use (0=first GPU)
GPU_MEMORY_FRACTION = 0.8  # Max fraction of GPU memory to use

# Async Processing
ENABLE_ASYNC_PROCESSING = False  # Experimental: async pipeline
NUM_WORKER_THREADS = 2  # Worker threads for async processing

# Memory & Performance
OPTIMIZE_MEMORY = True  # Release unused memory aggressively
OCR_BATCH_SIZE = 3  # Process N textboxes in parallel (OCR)
SKIP_SMALL_TEXTBOXES = False  # Skip boxes < 50px (too small to read)
MIN_TEXTBOX_SIZE = 30  # Minimum textbox size in pixels
