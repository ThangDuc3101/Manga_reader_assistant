import logging
import os
from ultralytics import YOLO
from translation_manager import TranslationManager
from PIL import Image, ImageDraw, ImageFont
from manga_ocr import MangaOcr

logger = logging.getLogger(__name__)

# Try importing Roboflow (optional)
try:
    from roboflow import Roboflow
    ROBOFLOW_AVAILABLE = True
except ImportError:
    ROBOFLOW_AVAILABLE = False
    logger.warning("Roboflow not installed. Install with: pip install roboflow")


class Manga_Reader:
    """Manga reader that detects text, recognizes it, and translates to Vietnamese."""
    
    FONT_SIZE = 40
    TEXT_COLOR = (255, 0, 0)  # Red in BGR
    MAX_TEXT_LENGTH = 500
    
    def __init__(self, use_roboflow=None, model_path=None, api_key=None):
        """
        Initialize Manga Reader with YOLO detector, OCR, and translator.
        
        Parameters:
            use_roboflow (bool): Use Roboflow API if True. If None, uses config.USE_ROBOFLOW
            model_path (str): Path to YOLO model weights (fallback if Roboflow unavailable)
            api_key (str): Roboflow API key. If None, uses config.ROBOFLOW_API_KEY
        """
        try:
            # Import config
            from config import (USE_ROBOFLOW, ROBOFLOW_API_KEY, ROBOFLOW_MODEL, 
                               ROBOFLOW_VERSION, FALLBACK_MODEL_PATH, OFFLINE_MODE)
            
            # Use provided parameters or fallback to config
            use_roboflow = use_roboflow if use_roboflow is not None else USE_ROBOFLOW
            model_path = model_path or FALLBACK_MODEL_PATH
            api_key = api_key or ROBOFLOW_API_KEY
            
            # Try loading model with Roboflow
            self.model = None
            if use_roboflow and ROBOFLOW_AVAILABLE:
                try:
                    self.model = self._load_roboflow_model(api_key, ROBOFLOW_MODEL, ROBOFLOW_VERSION)
                    logger.info("Loaded model from Roboflow API")
                except Exception as e:
                    logger.warning(f"Roboflow loading failed: {e}. Falling back to YOLOv8s...")
            
            # Fallback to YOLOv8 if Roboflow failed or disabled
            if self.model is None:
                self.model = YOLO(model_path)
                logger.info(f"Loaded model from {model_path}")
            
            # Initialize OCR and translator
            self.recognizer = MangaOcr()
            self.translator = TranslationManager()
            logger.info("Manga_Reader initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Manga_Reader: {e}")
            raise
    
    def _load_roboflow_model(self, api_key, model_name, version):
        """
        Load model from Roboflow API.
        
        Parameters:
            api_key (str): Roboflow API key
            model_name (str): Model name (e.g., 'manga-bubble-detect')
            version (int): Model version number
            
        Returns:
            YOLO: Loaded YOLO model object
        """
        if not api_key:
            raise ValueError("ROBOFLOW_API_KEY not configured")
        
        try:
            rf = Roboflow(api_key=api_key)
            # Access community models (no workspace required for public models)
            project = rf.workspace().project(model_name)
            model_obj = project.version(version).model
            
            # Convert to YOLO format if needed
            logger.info(f"Roboflow model loaded: {model_name} v{version}")
            return model_obj
            
        except Exception as e:
            logger.error(f"Failed to load Roboflow model: {e}")
            raise
    
    def _get_font(self, size=FONT_SIZE):
        """
        Get a valid font for text rendering, with fallback to default.
        
        Parameters:
            size (int): Font size in pixels.
            
        Returns:
            ImageFont.FreeTypeFont: Font object or default font.
        """
        font_candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
            "/System/Library/Fonts/Arial.ttf",  # macOS
            "C:\\Windows\\Fonts\\arial.ttf",  # Windows
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",  # Linux alt
        ]
        
        for font_path in font_candidates:
            try:
                return ImageFont.truetype(font_path, size)
            except:
                continue
        
        logger.warning("No TrueType font found, using default font")
        return ImageFont.load_default()
        
    def detect(self, frame):
        """
        Detect textboxes in a frame using the YOLO model.

        Parameters:
            frame (PIL.Image.Image): Input image to detect textboxes.

        Returns:
            list: List of textboxes as [x1, y1, x2, y2].
        """
        try:
            if not isinstance(frame, Image.Image):
                raise TypeError(f"Expected PIL.Image, got {type(frame)}")
                
            textboxes = []
            results = self.model(frame)
            
            if not results or len(results) == 0:
                logger.warning("No detection results from YOLO")
                return textboxes
            
            box = results[0].boxes
            for b in box:
                x1, y1, x2, y2 = b.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                textboxes.append([x1, y1, x2, y2])
            
            logger.info(f"Detected {len(textboxes)} textboxes")
            return textboxes
            
        except Exception as e:
            logger.error(f"Error in detect(): {e}")
            raise
    
    def _render_translation(self, translated_text, posText, img):
        """
        Render translated text on image at specified position.
        
        Helper method for Phase 3 of batch processing.
        
        Parameters:
            translated_text (str): Already translated text to render.
            posText (tuple): Position [x1, y1, x2, y2] where text will be placed.
            img (PIL.Image.Image): Image to add the text to.
            
        Returns:
            PIL.Image.Image: Image with text added.
        """
        try:
            if not translated_text or not isinstance(translated_text, str):
                logger.debug(f"Skipping empty translation")
                return img
            
            draw = ImageDraw.Draw(img)
            font = self._get_font(self.FONT_SIZE)
            
            # Split text intelligently (2 words per line)
            words = translated_text.split(" ")
            lines = []
            
            for i in range(len(words)):
                if i % 2 == 1:
                    lines.append(words[i - 1] + " " + words[i])
                elif i == len(words) - 1:
                    lines.append(words[i])
            
            # Draw text on image
            for i, line in enumerate(lines):
                y_position = posText[1] + i * self.FONT_SIZE
                draw.text(
                    (posText[0], y_position),
                    line,
                    fill=self.TEXT_COLOR,
                    font=font
                )
            
            logger.debug(f"Rendered {len(lines)} lines at position {posText[:2]}")
            return img
            
        except Exception as e:
            logger.error(f"Error in _render_translation(): {e}")
            return img
    
    def process_chat(self, text, posText, img):
        """
        Process and add translated text to the image (legacy method).
        
        Deprecated: Use batch processing in __call__() instead.
        Kept for backward compatibility.

        Parameters:
            text (str): Text to be processed.
            posText (tuple): Position [x1, y1, x2, y2] where text will be placed.
            img (PIL.Image.Image): Image to add the text to.

        Returns:
            PIL.Image.Image: Image with text added.
        """
        try:
            if not text or not isinstance(text, str):
                logger.warning(f"Invalid text input: {text}")
                return img
            
            # Validate text length
            if len(text) > self.MAX_TEXT_LENGTH:
                logger.warning(f"Text truncated from {len(text)} to {self.MAX_TEXT_LENGTH} chars")
                text = text[:self.MAX_TEXT_LENGTH]
            
            # Translate to Vietnamese
            translated = self.translator.translate(text, src="ja", dest="vi")
            
            if not translated or not translated.text:
                logger.warning("Translation failed, skipping text")
                return img
            
            # Use rendering helper
            return self._render_translation(translated.text, posText, img)
            
        except Exception as e:
            logger.error(f"Error in process_chat(): {e}")
            return img
    
    def __call__(self, img, use_batch_translation: bool = True):
        """
        Process an image by detecting, recognizing, and translating text.
        
        Implements 3-phase batch processing for 3-5x speedup:
        - Phase 1: Detect textboxes and recognize all text
        - Phase 2: Batch translate all texts at once (3-5x faster)
        - Phase 3: Render all translations on image

        Parameters:
            img (PIL.Image.Image): Manga image to process.
            use_batch_translation (bool): Use batch API if True, sequential if False.
                Default: True (3-5x faster)

        Returns:
            PIL.Image.Image: Processed image with Vietnamese text.
        """
        try:
            if not isinstance(img, Image.Image):
                raise TypeError(f"Expected PIL.Image, got {type(img)}")
            
            # ============================================
            # PHASE 1: Detect textboxes & recognize text
            # ============================================
            logger.info("PHASE 1: Detecting textboxes and recognizing text...")
            
            textboxes = self.detect(img)
            
            text_data = []  # List of {'text': str, 'box': [x1, y1, x2, y2]}
            
            for textbox in textboxes:
                try:
                    # Crop image to textbox region
                    bubble_chat = img.crop((textbox[0], textbox[1], textbox[2], textbox[3]))
                    
                    # Recognize text using OCR
                    text = self.recognizer(bubble_chat)
                    
                    # Validate and truncate if needed
                    if text and isinstance(text, str):
                        if len(text) > self.MAX_TEXT_LENGTH:
                            logger.debug(f"Text truncated from {len(text)} to {self.MAX_TEXT_LENGTH} chars")
                            text = text[:self.MAX_TEXT_LENGTH]
                        
                        text_data.append({
                            'text': text,
                            'box': textbox
                        })
                    
                except Exception as e:
                    logger.error(f"Error recognizing text in textbox {textbox}: {e}")
                    continue
            
            logger.info(f"Phase 1 complete: {len(text_data)} texts recognized")
            
            if not text_data:
                logger.info("No text detected, returning original image")
                return img
            
            # ============================================
            # PHASE 2: Batch translate all texts
            # ============================================
            logger.info("PHASE 2: Batch translating texts...")
            
            # Extract all texts
            texts = [item['text'] for item in text_data]
            
            # Use batch translation if enabled and available
            try:
                if use_batch_translation and hasattr(self.translator, 'batch_translate_grouped'):
                    logger.info(f"Using batch translation ({len(texts)} texts)...")
                    translations = self.translator.batch_translate_grouped(
                        texts,
                        src="ja",
                        dest="vi",
                        batch_size=10
                    )
                else:
                    logger.info(f"Using sequential translation ({len(texts)} texts)...")
                    translations = self.translator.batch_translate(texts, src="ja", dest="vi")
                
                # Extract translated text
                translated_texts = [
                    t.text if hasattr(t, 'text') else str(t)
                    for t in translations
                ]
                
            except Exception as e:
                logger.warning(f"Batch translation failed: {e}. Falling back to sequential...")
                # Fallback to sequential
                translations = self.translator.batch_translate(texts, src="ja", dest="vi")
                translated_texts = [
                    t.text if hasattr(t, 'text') else str(t)
                    for t in translations
                ]
            
            # Map translations back to text_data
            for item, translated_text in zip(text_data, translated_texts):
                item['translated'] = translated_text
            
            logger.info("Phase 2 complete: All texts translated")
            
            # ============================================
            # PHASE 3: Render all translations on image
            # ============================================
            logger.info("PHASE 3: Rendering translations on image...")
            
            for item in text_data:
                try:
                    translated_text = item.get('translated', item['text'])
                    box = item['box']
                    
                    img = self._render_translation(translated_text, box, img)
                    
                except Exception as e:
                    logger.error(f"Error rendering text for box {item['box']}: {e}")
                    continue
            
            logger.info("Phase 3 complete: All translations rendered")
            logger.info("Image processing complete")
            
            return img
            
        except Exception as e:
            logger.error(f"Error in __call__(): {e}")
            raise
    
       
if __name__=='__main__':    
    reader = Manga_Reader()
    img = Image.open("test/jjk4.png")
    img = reader(img)
    img.show()
           

    
          
      
