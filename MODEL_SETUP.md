# 🤖 Model Setup Guide - Roboflow Manga Bubble Detector

**Status**: Phase 1 Updated | Model Migration Complete  
**Last Updated**: 2024-12-10  
**Recommended**: Roboflow API (free, easy, maintained)

---

## 📋 TABLE OF CONTENTS

1. [Quick Start](#quick-start)
2. [Roboflow Setup](#roboflow-setup)
3. [Configuration Options](#configuration-options)
4. [Offline Usage (Download Weights)](#offline-usage-download-weights)
5. [Fallback Options](#fallback-options)
6. [Troubleshooting](#troubleshooting)

---

## ⚡ Quick Start

### Option 1: Roboflow API (Recommended - 5 minutes)

```bash
# 1. Install Roboflow SDK
pip install roboflow

# 2. Set API key in config.py (see Configuration section below)
# ROBOFLOW_API_KEY = "your_api_key_here"

# 3. Test the setup
python3 -c "from reader import Manga_Reader; reader = Manga_Reader(); print('✓ Model loaded')"

# 4. Run the app
streamlit run main.py
```

### Option 2: Offline with Weights (After API setup)

```bash
# 1. Download weights once from Roboflow
python3 -c "
from reader import Manga_Reader
reader = Manga_Reader()  # Downloads weights automatically
print('✓ Weights cached locally')
"

# 2. Run app without internet (afterwards)
OFFLINE_MODE=1 streamlit run main.py
```

---

## 🎯 Roboflow Setup (Step-by-Step)

### Step 1: Create Roboflow Account

1. Go to [roboflow.com](https://roboflow.com)
2. Sign up for free account
3. Create new workspace (or use default)

### Step 2: Get API Key

1. Navigate to **Settings** → **Roboflow API**
2. Copy your **Private API Key**
3. Keep it safe (don't commit to git)

### Step 3: Find Manga Bubble Detector Model

The model we use:
- **Project**: `manga-bubble-detect`
- **Workspace**: Community public models (no login required for inference)

Or search for similar models:
- Go to **Models** in Roboflow
- Search "manga" or "bubble"
- Look for trained YOLOv8 models

### Step 4: Configure in config.py

```python
# In config.py, set:
ROBOFLOW_API_KEY = "your_private_api_key_here"
ROBOFLOW_MODEL = "manga-bubble-detect"  # Or your custom model
ROBOFLOW_VERSION = 1  # Check your model version
USE_ROBOFLOW = True  # Enable Roboflow API
```

### Step 5: Test Configuration

```bash
python3 -c "
from config import ROBOFLOW_API_KEY, ROBOFLOW_MODEL
print(f'API Key: {ROBOFLOW_API_KEY[:10]}...')
print(f'Model: {ROBOFLOW_MODEL}')
print('✓ Configuration loaded')
"
```

---

## ⚙️ Configuration Options

### In config.py

```python
# ============================================================================
# ROBOFLOW MODEL CONFIGURATION
# ============================================================================

# Enable/disable Roboflow API
USE_ROBOFLOW = True

# Roboflow API credentials
ROBOFLOW_API_KEY = "your_api_key_here"  # Get from https://roboflow.com/settings/api

# Model selection
ROBOFLOW_MODEL = "manga-bubble-detect"  # Public model or your custom model
ROBOFLOW_VERSION = 1  # Model version number

# Fallback model (if Roboflow fails or offline)
FALLBACK_MODEL_PATH = "yolov8s.pt"  # YOLOv8s base model (auto-downloads)

# Offline mode (use cached weights, no API calls)
OFFLINE_MODE = False  # Set True after downloading weights

# Cache location for downloaded weights
MODEL_CACHE_DIR = ".models"  # Where to store downloaded model weights
```

### Environment Variables (Alternative)

Instead of hardcoding API key, use environment variables:

```bash
# Set before running app
export ROBOFLOW_API_KEY="your_api_key_here"
export ROBOFLOW_MODEL="manga-bubble-detect"

# Then in config.py
import os
ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY")
ROBOFLOW_MODEL = os.getenv("ROBOFLOW_MODEL", "manga-bubble-detect")
```

### .env File (Recommended for Development)

1. Create `.env` file in project root:

```bash
ROBOFLOW_API_KEY=your_api_key_here
ROBOFLOW_MODEL=manga-bubble-detect
ROBOFLOW_VERSION=1
```

2. Load in main.py or config.py:

```python
from dotenv import load_dotenv
import os

load_dotenv()  # Load from .env
ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY")
```

3. Add `.env` to `.gitignore`:

```bash
echo ".env" >> .gitignore
```

---

## 📦 Offline Usage (Download Weights)

After using Roboflow API once, you can download weights for offline use.

### Step 1: Download Weights (One-time)

```bash
python3 << 'EOF'
from reader import Manga_Reader
import os

reader = Manga_Reader()
print("✓ Model downloaded and cached")

# Check cache location
cache_dir = ".models"
if os.path.exists(cache_dir):
    print(f"Cached models in: {cache_dir}/")
    import subprocess
    subprocess.run(["ls", "-lh", cache_dir])
EOF
```

### Step 2: Enable Offline Mode

```python
# In config.py, set:
OFFLINE_MODE = True
USE_ROBOFLOW = False  # Don't call API

# App will use cached weights from MODEL_CACHE_DIR
```

### Step 3: Run Offline

```bash
# No internet needed now
OFFLINE_MODE=1 streamlit run main.py
```

---

## 🔄 Fallback Options

The application has multiple fallback levels:

### Level 1: Roboflow API (Primary)
```
✓ Best accuracy
✓ Actively maintained
✓ Easy to update models
✗ Requires internet + API key
```

### Level 2: Cached Weights (Downloaded from Roboflow)
```
✓ Offline capable
✓ Good accuracy
✓ Fast loading
✗ Need to download once first
```

### Level 3: YOLOv8s Base Model (Fallback)
```
✓ No download needed (auto-downloaded by Ultralytics)
✓ Works offline after first run
✓ Universal YOLO model
✗ Less optimized for manga
```

**Automatic Fallback Flow**:
```
1. Try Roboflow API
   ↓ (if fails)
2. Try cached weights from .models/
   ↓ (if not found)
3. Use yolov8s.pt (auto-download)
   ↓ (if all fails)
4. Return empty detections, show error
```

---

## 🔧 Troubleshooting

### Problem: "API key invalid" or "Authentication failed"

**Solution**:
```bash
# 1. Verify API key is correct
echo $ROBOFLOW_API_KEY

# 2. Check format (should be alphanumeric)
# 3. Regenerate key at https://roboflow.com/settings/api
# 4. Update in config.py or .env
```

### Problem: "Model not found"

**Solution**:
```bash
# 1. Check model name and version
python3 -c "from config import ROBOFLOW_MODEL; print(ROBOFLOW_MODEL)"

# 2. Verify model exists on Roboflow
#    Go to https://roboflow.com/workspace/models
#    Check project name matches

# 3. Use fallback model:
#    Set USE_ROBOFLOW = False in config.py
```

### Problem: "Network timeout" or slow detection

**Solution**:
```bash
# 1. Download weights for offline use (see above)
# 2. Set OFFLINE_MODE = True
# 3. Or increase timeout in config.py:
ROBOFLOW_TIMEOUT = 60  # seconds
```

### Problem: "ModuleNotFoundError: roboflow"

**Solution**:
```bash
# Install Roboflow SDK
pip install roboflow

# Or update all dependencies
pip install -r requirements.txt
```

---

## 📊 Model Specifications

### Roboflow Manga Bubble Detector

| Attribute | Value |
|-----------|-------|
| **Framework** | YOLOv8 |
| **Input Size** | 640x640 |
| **Training Data** | 4,492 manga images |
| **Classes** | Bubble (speech/thought/narrative) |
| **Accuracy** | ~95% mAP |
| **Speed** | ~50ms per image |
| **License** | Community (open for use) |

### Fallback Model: YOLOv8s

| Attribute | Value |
|-----------|-------|
| **Framework** | YOLOv8 |
| **Input Size** | 640x640 |
| **Training Data** | COCO dataset |
| **Classes** | General objects (80 classes) |
| **Accuracy** | ~44.9% mAP on COCO |
| **Speed** | ~15ms per image |
| **Size** | ~10MB |

---

## 🌍 Model Download Sources

### Primary: Roboflow API
- **URL**: roboflow.com
- **Model**: manga-bubble-detect (public)
- **Authentication**: API key (free)
- **Speed**: Fast, reliable

### Fallback: Ultralytics
- **URL**: ultralytics.com
- **Model**: yolov8s (auto-download)
- **Authentication**: None required
- **Speed**: General purpose

### Custom Models
To use your own trained model:

```python
# In config.py
ROBOFLOW_MODEL = "your-custom-model"
ROBOFLOW_VERSION = 5  # Your version number
```

---

## 📝 Integration with Application

### In reader.py

The `Manga_Reader` class now supports:

```python
from reader import Manga_Reader

# Load with Roboflow API
reader = Manga_Reader(use_roboflow=True)

# Load with cached weights
reader = Manga_Reader(use_roboflow=False, offline=True)

# Load with fallback model
reader = Manga_Reader(model_path="yolov8s.pt")
```

### In config.py

Add to requirements.txt:
```
roboflow==0.2.0
python-dotenv==1.0.0  # For .env file support
```

---

## 🚀 Deployment Checklist

Before deploying to production:

- [ ] API key securely stored (not in git)
- [ ] Use .env file or environment variables
- [ ] Test with sample manga images
- [ ] Verify fallback model works
- [ ] Document model source for team
- [ ] Set up rate limiting if needed
- [ ] Monitor API usage on Roboflow dashboard
- [ ] Have offline weights downloaded as backup

---

## 📞 Support & Resources

### Roboflow Documentation
- **Main Docs**: https://docs.roboflow.com
- **API Reference**: https://docs.roboflow.com/api-reference/introduction
- **Model Hub**: https://roboflow.com/models

### Manga Bubble Detection
- **Public Model**: Search "manga" on Roboflow
- **Community Models**: https://roboflow.com/workspace/models
- **Training Your Own**: https://docs.roboflow.com/train

### YOLOv8 Documentation
- **Official Docs**: https://docs.ultralytics.com
- **Models**: https://github.com/ultralytics/ultralytics

---

## 🔗 Next Steps

1. ✅ [Roboflow Setup](#roboflow-setup) - Create account & get API key
2. ✅ [Configure in config.py](#configuration-options) - Add API key
3. ✅ Test with sample image
4. ✅ [Optional] Download weights for offline use
5. ✅ Deploy to production

---

**Last Updated**: 2024-12-10  
**Status**: Migration Complete ✅ | Ready for Production 🚀  
**Model**: Roboflow Manga Bubble Detector + YOLOv8s Fallback
