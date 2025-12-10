# Setup Guide - Manga Reader Assistant (After Critical Fixes)

## 📋 Prerequisites

- **Python**: 3.10 or higher
- **OS**: Windows, macOS, or Linux
- **RAM**: 8GB+ (for YOLO model loading)
- **GPU** (optional): CUDA 11.0+ for faster processing
- **Internet**: Required for Google Translate API on first use

---

## 🔧 Step-by-Step Installation

### 1. Clone/Download Repository
```bash
git clone https://github.com/ThangDuc3101/Manga_reader_assistant.git
cd Manga_reader_assistant
```

### 2. Create Virtual Environment (Recommended)
```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Or using conda
conda create -n manga-reader python=3.10
conda activate manga-reader
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

**Note**: First install will take 5-10 minutes (downloads ML models).

### 4. Download YOLO Model Weights
Download from: https://drive.google.com/file/d/1-XpMOB8wN1j1d57iq6JBLyzAQlPmyLoV/view?usp=drive_link

Save file as `yolov8_manga.pt` in project root:
```
Manga_reader_assistant/
├── yolov8_manga.pt     ← Place downloaded file here
├── main.py
├── reader.py
└── ...
```

### 5. Verify Installation
```bash
# Test Python imports
python -c "import streamlit; import ultralytics; import manga_ocr; print('✓ All imports OK')"

# Check YOLO model
python -c "from ultralytics import YOLO; YOLO('yolov8_manga.pt'); print('✓ Model loaded')"
```

---

## 🚀 Running the Application

### Start App
```bash
streamlit run main.py
```

Expected output:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
```

### Access Web UI
- Open browser: http://localhost:8501
- Streamlit will automatically reload on code changes
- Stop with: `Ctrl+C` in terminal

---

## 📝 Configuration

### Using config.py
Edit `config.py` to customize:

```python
# Change target language
TARGET_LANGUAGE = "vi"  # Vietnamese

# Change font size
FONT_SIZE = 40

# Change output directory
OUTPUT_DIR = 'translated'

# Enable debug mode
DEBUG_MODE = True
```

Changes take effect on next app restart.

---

## 🎯 Usage

### Step 1: Navigate to "Assistant" Tab
Click "Assistant" from the left sidebar.

### Step 2: Upload Manga Images
- Click "Upload manga images" in sidebar
- Select one or multiple images (JPG, PNG, BMP, WebP)
- Max size: 50MB per file

### Step 3: Wait for Processing
The app will:
1. Load YOLO model (first time: ~10 seconds)
2. Detect text boxes in manga
3. Recognize Japanese text using OCR
4. Translate to Vietnamese
5. Render translations on image
6. Save result to `translated/` folder

### Step 4: View Results
- Translated images displayed in main area
- Success message shows save location
- Download if needed

### Step 5: View Saved Images
- Go to "Read Only" tab
- Upload previously saved images
- View without reprocessing

---

## ⚙️ Advanced Configuration

### Use Google Cloud Translation API (More Stable)
Instead of unofficial `googletrans`:

```bash
# 1. Install Google Cloud SDK
pip install google-cloud-translate

# 2. Set up authentication
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"

# 3. Enable in config.py
USE_GOOGLE_CLOUD_API = True
GOOGLE_CLOUD_PROJECT_ID = "your-project-id"
```

### Enable GPU Acceleration (CUDA)
```bash
# Install CUDA 11.0+ from https://developer.nvidia.com/cuda-downloads

# Install PyTorch with CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Restart app - YOLO will auto-detect GPU
```

### Change YOLO Model Size
```python
# In reader.py, change:
self.model = YOLO("yolov8_manga.pt")  # Current

# To one of:
self.model = YOLO("yolov8n_manga.pt")  # Nano (fast, less accurate)
self.model = YOLO("yolov8s_manga.pt")  # Small
self.model = YOLO("yolov8m_manga.pt")  # Medium
self.model = YOLO("yolov8l_manga.pt")  # Large (current)
self.model = YOLO("yolov8x_manga.pt")  # Extra Large (slow, most accurate)
```

---

## 🐛 Troubleshooting

### Issue: "Model file not found"
```
Error: yolov8_manga.pt not found
```
**Solution**: 
- Download model from link in README
- Save as `yolov8_manga.pt` in project root
- Run from correct directory

### Issue: "No TrueType font found"
```
Warning: No TrueType font found, using default font
```
**Solution** (optional, app still works):
- Linux: `sudo apt-get install fonts-dejavu`
- macOS: Fonts should be pre-installed
- Windows: Fonts should be pre-installed

### Issue: "Font size too large / illegible"
**Solution**:
- Edit `config.py`:
```python
FONT_SIZE = 30  # Reduce from 40
```

### Issue: "Translation API blocked / rate limited"
```
Error: google.cloud.exception.GoogleCloudError
```
**Solution**:
- Wait a few minutes before retrying
- Switch to Google Cloud API (more reliable)
- Batch fewer texts at once

### Issue: "Out of Memory"
```
RuntimeError: CUDA out of memory
```
**Solutions**:
1. Reduce image size before uploading
2. Close other applications
3. Use smaller YOLO model: `yolov8n_manga.pt`
4. Run on CPU: Set `DEVICE="cpu"` in config

### Issue: "Slow processing"
**Solutions**:
1. First image is slowest (model loading) - normal
2. Enable GPU acceleration if available
3. Use smaller YOLO model
4. Reduce image resolution

---

## 📊 Performance Expectations

| Step | Time | Notes |
|------|------|-------|
| Model loading | 5-10s | Only first image, then cached |
| Text detection (YOLO) | 2-5s | Varies with image size |
| Text recognition (OCR) | 3-8s | Depends on number of textboxes |
| Translation | 2-5s | Depends on text length, API speed |
| **Total (first image)** | **15-30s** | Mostly waiting for APIs |
| **Total (subsequent)** | **5-15s** | Model already cached |

---

## 🔍 Logging & Debugging

### View Logs
Logs appear in terminal where you ran `streamlit run main.py`.

Example:
```
2024-12-10 10:30:45 - reader - INFO - Manga_Reader initialized successfully
2024-12-10 10:30:46 - reader - INFO - Detected 12 textboxes
2024-12-10 10:30:48 - reader - INFO - Processed 3 lines of text
```

### Enable Debug Mode
Edit `config.py`:
```python
DEBUG_MODE = True
LOG_LEVEL = "DEBUG"
SAVE_INTERMEDIATES = True
```

This will:
- Show more detailed logs
- Save intermediate images (detection masks, crops)
- Disable model caching (fresh load each time)

---

## 📦 Project Structure

```
Manga_reader_assistant/
├── main.py              # Entry point (navigation menu)
├── reader.py            # YOLO + OCR + Translation logic
├── assistant.py         # Streamlit UI for translation
├── readOnly.py          # Streamlit UI for viewing results
├── about.py             # Project info page
├── config.py            # Configuration file (NEW)
├── requirements.txt     # Python dependencies
├── CRITICAL_FIXES.md    # What was fixed (NEW)
├── SETUP_GUIDE.md       # This file (NEW)
│
├── yolov8_manga.pt      # YOLO model weights (download)
├── translated/          # Output folder (auto-created)
├── test/                # Test images
├── img/                 # Documentation images
└── font/                # Font files (if custom fonts)
```

---

## 📚 Next Steps

### After Successful Setup

1. **Test with sample images** in `test/` folder:
   ```bash
   # Upload test/jjk4.png to try it out
   ```

2. **Customize settings** in `config.py`:
   - Font size, color
   - Languages
   - Output format

3. **Explore Phase 2 improvements** (see CRITICAL_FIXES.md)

---

## 🆘 Getting Help

If you encounter issues:

1. **Check terminal logs** - error messages are detailed
2. **Read CRITICAL_FIXES.md** - known issues and solutions
3. **Check issue tracker** - https://github.com/ThangDuc3101/Manga_reader_assistant/issues
4. **Common problems**: See "Troubleshooting" section above

---

## 💡 Tips & Tricks

### Batch Processing Multiple Folders
```bash
# Create script to process all images in a folder
for image in /path/to/manga/*.png; do
  echo "Processing: $image"
  # Use Python reader.py directly
done
```

### Command-Line Usage (Advanced)
```python
from reader import Manga_Reader
from PIL import Image

# Load and process
reader = Manga_Reader()
image = Image.open("manga_page.png")
result = reader(image)
result.save("translated.png")
```

### API Rate Limiting (if hitting limits)
```python
# In config.py
BATCH_SIZE = 5  # Translate 5 texts at once instead of 10
TRANSLATION_API_TIMEOUT = 60  # Wait longer between requests
```

---

## 📞 Support & Feedback

- **Author**: ThangBui
- **Repository**: https://github.com/ThangDuc3101/Manga_reader_assistant
- **Email**: [Contact author via GitHub]

---

## ✅ Checklist for Successful Setup

- [ ] Python 3.10+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Model file `yolov8_manga.pt` downloaded and placed
- [ ] Imports verified successfully
- [ ] App starts without errors (`streamlit run main.py`)
- [ ] Can upload test image without crashes
- [ ] Translation appears in output
- [ ] Output saved to `translated/` folder

**All checked? You're ready to translate manga!** 🎉
