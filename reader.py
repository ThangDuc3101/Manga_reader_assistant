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
    
    def process_chat(self, text, posText, img):
        """
        Process and add translated text to the image.

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
            
            draw = ImageDraw.Draw(img)
            font = self._get_font(self.FONT_SIZE)
            
            # Split text intelligently (2 words per line)
            chat = translated.text.split(" ")
            content = []
            
            for i in range(len(chat)):
                if i % 2 == 1:
                    content.append(chat[i - 1] + " " + chat[i])
                elif i == len(chat) - 1:  # Fixed: was using & instead of 'and'
                    content.append(chat[i])
            
            # Draw text on image
            for i, line in enumerate(content):
                y_position = posText[1] + i * self.FONT_SIZE
                draw.text(
                    (posText[0], y_position),
                    line,
                    fill=self.TEXT_COLOR,
                    font=font
                )
            
            logger.info(f"Processed {len(content)} lines of text")
            return img
            
        except Exception as e:
            logger.error(f"Error in process_chat(): {e}")
            return img
    
    def __call__(self, img):
        """
        Process an image by detecting, recognizing, and translating text.

        Parameters:
            img (PIL.Image.Image): Manga image to process.

        Returns:
            PIL.Image.Image: Processed image with Vietnamese text.
        """
        try:
            if not isinstance(img, Image.Image):
                raise TypeError(f"Expected PIL.Image, got {type(img)}")
            
            textboxes = self.detect(img)
            
            for textbox in textboxes:
                try:
                    # Crop image to textbox region
                    bubble_chat = img.crop((textbox[0], textbox[1], textbox[2], textbox[3]))
                    
                    # Recognize text using OCR
                    text = self.recognizer(bubble_chat)
                    
                    # Process and add to image
                    img = self.process_chat(text, textbox, img)
                    
                except Exception as e:
                    logger.error(f"Error processing textbox {textbox}: {e}")
                    continue
            
            return img
            
        except Exception as e:
            logger.error(f"Error in __call__(): {e}")
            raise
    
       
if __name__=='__main__':    
    reader = Manga_Reader()
    img = Image.open("test/jjk4.png")
    img = reader(img)
    img.show()
           

    
          
      
