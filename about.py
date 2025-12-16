import streamlit as st
from PIL import Image
import logging
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def app():
    """
    Display information about the Manga Reader Assistant project.
    
    Shows project overview, architecture, and technologies used.
    """
    
    try:
        st.title("MANGA READER")
        st.text("Author: ThangBui")
        st.text("Framework: Ultralytics, OCR, Streamlit")
        
        st.header("📖 Project Information")
        st.write(
            "This project was created to read Japanese manga in Vietnamese. "
            "The system uses Computer Vision and AI to automatically detect, "
            "recognize, and translate manga text."
        )
        
        st.divider()
        
        # Architecture Overview
        st.header("🏗️ Architecture")
        st.write(
            """
            **Processing Pipeline:**
            1. **Detection** → Roboflow API detects speech bubbles using YOLOv8-based model
            2. **OCR** → Manga-OCR recognizes Japanese text in bubbles
            3. **Translation** → Google Translator converts Japanese to Vietnamese
            4. **Rendering** → Translated text is rendered back on the image
            """
        )
        
        st.divider()
        
        # Model Information
        st.header("🤖 Detection Model")
        try:
            if os.path.exists("img/pruning_model.png"):
                model_img = Image.open("img/pruning_model.png")
                st.image(model_img, use_column_width=True)
                logger.info("Displayed model image")
            else:
                st.warning("Model image not found")
        except Exception as e:
            st.warning(f"Cannot load model image: {str(e)}")
            logger.warning(f"Error loading model image: {e}")
        
        st.write(
            "**Roboflow Model:** `manga-bubble-pqdou/1`\n\n"
            "The model is based on YOLOv8 architecture, fine-tuned specifically "
            "for detecting text bubbles and speech boxes in manga."
        )
        
        st.divider()
        
        # OCR Information
        st.header("🔤 Optical Character Recognition (OCR)")
        st.write(
            "**Manga-OCR** - Specialized OCR for Japanese manga text\n\n"
            "This library is specifically designed for recognizing Japanese characters "
            "in manga, handling unique fonts and layouts typical of manga."
        )
        st.link_button(
            "View Manga-OCR Source",
            "https://github.com/kha-white/manga-ocr"
        )
        
        st.divider()
        
        # Translation Information
        st.header("🌐 Translation")
        st.write(
            "**Google Translator (deep-translator)**\n\n"
            "Reliable translation service with retry mechanism for stability. "
            "Translates from Japanese (ja) to Vietnamese (vi)."
        )
        
        st.divider()
        
        # Features
        st.header("✨ Features")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(
                "✅ Batch processing multiple images\n"
                "✅ Automatic speech bubble detection\n"
                "✅ Japanese text recognition"
            )
        
        with col2:
            st.write(
                "✅ Automatic translation to Vietnamese\n"
                "✅ Responsive text rendering\n"
                "✅ Error handling & retry mechanism"
            )
        
        st.divider()
        
        # Requirements
        st.header("📦 Technologies")
        st.write(
            """
            - **YOLOv8**: Object detection via Roboflow API
            - **Manga-OCR**: Japanese text recognition
            - **Deep-Translator**: Japanese to Vietnamese translation with retry
            - **Streamlit**: Web UI framework
            - **PIL**: Image processing
            - **Tenacity**: Retry mechanism
            """
        )
        
        st.divider()
        
        # Version & Updates
        st.header("📝 Latest Updates (Phase 2)")
        st.write(
            """
            **Stability Improvements:**
            - ✅ Replaced unstable `googletrans` with `deep-translator`
            - ✅ Added retry mechanism with exponential backoff
            - ✅ Comprehensive error handling throughout codebase
            - ✅ Model caching to improve performance
            - ✅ Better logging and user feedback
            - ✅ Responsive text rendering based on textbox size
            - ✅ Clear original text before rendering translation
            """
        )
        
        logger.info("About page displayed successfully")
    
    except Exception as e:
        st.error(f"Error displaying about page: {str(e)}")
        logger.error(f"Error in about.app(): {e}")
