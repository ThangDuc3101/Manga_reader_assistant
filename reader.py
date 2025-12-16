from deep_translator import GoogleTranslator
from PIL import Image, ImageDraw, ImageFont
from manga_ocr import MangaOcr
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential
import os
import requests
import base64
from io import BytesIO
import logging
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Supported languages for translation
SUPPORTED_LANGUAGES = {
    'vi': 'Vietnamese',
    'en': 'English',
    'zh-CN': 'Chinese (Simplified)',
    'zh-TW': 'Chinese (Traditional)',
    'ko': 'Korean',
    'th': 'Thai',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'pt': 'Portuguese',
    'it': 'Italian',
    'ru': 'Russian',
}

class Manga_Reader:
    def __init__(self, detector=None, use_roboflow=True, target_language='vi'):
        """
        Initialize Manga Reader.
        
        Args:
            detector: Path to local YOLO model (if use_roboflow=False)
            use_roboflow: If True, use Roboflow API for detection
            target_language: Target language code (default: 'vi' for Vietnamese)
        """
        self.use_roboflow = use_roboflow
        self.target_language = target_language
        self.processing_stats = {
            'total_images': 0,
            'processed_images': 0,
            'total_textboxes': 0,
            'total_time': 0
        }
        
        try:
            if use_roboflow:
                # Roboflow API setup - su dung model manga-bubble-pqdou
                self.api_key = os.getenv("ROBOFLOW_API_KEY", "")
                if not self.api_key:
                    raise ValueError("ROBOFLOW_API_KEY not found. Please set it in .env file")
                self.model_id = "manga-bubble-pqdou/1"
                self.api_url = f"https://detect.roboflow.com/{self.model_id}"
                logger.info(f"Initialized Roboflow detection with model: {self.model_id}")
            else:
                # Local YOLO model
                if detector is None:
                    detector = "yolov8_manga.pt"
                from ultralytics import YOLO
                self.model = YOLO(detector)
                logger.info(f"Initialized local YOLO model: {detector}")
        except Exception as e:
            logger.error(f"Error initializing detection model: {e}")
            raise
        
        try:
            self.recognizer = MangaOcr()        # Manga-OCR
            logger.info("Manga-OCR initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Manga-OCR: {e}")
            raise
        
        try:
            self.translator = GoogleTranslator(source='ja', target=target_language)
            logger.info(f"Google Translator initialized for ja → {target_language} ({SUPPORTED_LANGUAGES.get(target_language, 'Unknown')})")
        except Exception as e:
            logger.error(f"Error initializing translator: {e}")
            raise
        
        # Font path - su dung duong dan tuyet doi
        self.font_path = os.path.join(os.path.dirname(__file__), "font", "arial.ttf")
        
        # Check if font exists
        if not os.path.exists(self.font_path):
            logger.warning(f"Font file not found at {self.font_path}")
        else:
            logger.info(f"Font file loaded: {self.font_path}")
    
    def set_target_language(self, language_code):
        """Change target language for translation."""
        try:
            if language_code not in SUPPORTED_LANGUAGES:
                logger.warning(f"Language {language_code} not supported. Using Vietnamese instead.")
                language_code = 'vi'
            
            self.target_language = language_code
            self.translator = GoogleTranslator(source='ja', target=language_code)
            logger.info(f"Changed target language to {language_code} ({SUPPORTED_LANGUAGES.get(language_code)})")
            return True
        except Exception as e:
            logger.error(f"Error changing language: {e}")
            return False
    
    def get_stats(self):
        """Get processing statistics."""
        return self.processing_stats.copy()
    
    def reset_stats(self):
        """Reset processing statistics."""
        self.processing_stats = {
            'total_images': 0,
            'processed_images': 0,
            'total_textboxes': 0,
            'total_time': 0
        }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def detect(self, frame):
        """
        Detects textboxes in a frame using the YOLO model. 

        Parameters:
            frame: the input frame to detect textboxes (PIL Image).

        Returns:
            A list of textboxes where each box is represented as [x1, y1, x2, y2].
        """
        textboxes = []
        
        try:
            if self.use_roboflow:
                # Roboflow REST API - convert image to base64
                # Convert RGBA to RGB if needed
                if frame.mode == 'RGBA':
                    frame = frame.convert('RGB')
                
                buffered = BytesIO()
                frame.save(buffered, format="JPEG")
                img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
                
                # Call Roboflow API
                response = requests.post(
                    self.api_url,
                    params={"api_key": self.api_key, "confidence": 40},
                    data=img_base64,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    timeout=30
                )
                response.raise_for_status()
                results = response.json()
                
                for prediction in results.get("predictions", []):
                    try:
                        x_center = prediction["x"]
                        y_center = prediction["y"]
                        width = prediction["width"]
                        height = prediction["height"]
                        
                        x1 = int(x_center - width / 2)
                        y1 = int(y_center - height / 2)
                        x2 = int(x_center + width / 2)
                        y2 = int(y_center + height / 2)
                        textboxes.append([x1, y1, x2, y2])
                    except KeyError as e:
                        logger.warning(f"Missing key in prediction: {e}")
                        continue
                
                logger.info(f"Detection: Found {len(textboxes)} textboxes")
            else:
                # Local YOLO model
                from ultralytics import YOLO
                results = self.model(frame)
                box = results[0].boxes
                for b in box:
                    x1, y1, x2, y2 = b.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    textboxes.append([x1, y1, x2, y2])
                
                logger.info(f"Detection: Found {len(textboxes)} textboxes")
        except requests.exceptions.RequestException as e:
            logger.error(f"Roboflow API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error during detection: {e}")
            raise
        
        return textboxes
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def translate_text(self, text):
        """
        Translate Japanese text to Vietnamese with retry mechanism.
        
        Args:
            text (str): Japanese text to translate
            
        Returns:
            str: Translated Vietnamese text
        """
        try:
            if not text or not text.strip():
                return text
            
            translated = self.translator.translate(text)
            logger.info(f"Translation: '{text[:30]}...' -> '{translated[:30]}...'")
            return translated
        except Exception as e:
            logger.error(f"Translation error: {e}")
            # Return original text if translation fails
            return text
    
    def wrap_text(self, text, font, max_width):
        """
        Wrap text to fit within max_width.
        
        Args:
            text (str): Text to wrap
            font: PIL font object
            max_width (int): Maximum width in pixels
            
        Returns:
            list: List of wrapped lines
        """
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " " if current_line else word + " "
            bbox = font.getbbox(test_line)
            line_width = bbox[2] - bbox[0]
            
            if line_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        return lines
    
    def calculate_font_size(self, text, box_width, box_height, max_font_size=40):
        """
        Calculate appropriate font size for text to fit in textbox.
        
        Args:
            text (str): Text to render
            box_width (int): Width of textbox
            box_height (int): Height of textbox
            max_font_size (int): Maximum font size to try
            
        Returns:
            int: Appropriate font size
        """
        try:
            font_size = max_font_size
            padding = 10  # Padding từ edge của textbox
            max_width = box_width - (padding * 2)
            max_height = box_height - (padding * 2)
            
            while font_size > 8:
                try:
                    font = ImageFont.truetype(self.font_path, font_size)
                    lines = self.wrap_text(text, font, max_width)
                    
                    # Tính tổng height của tất cả lines
                    bbox = font.getbbox("A")
                    line_height = bbox[3] - bbox[1]
                    total_height = len(lines) * (line_height + 3)  # 3px spacing
                    
                    if total_height <= max_height:
                        return font_size
                except Exception as e:
                    logger.warning(f"Error in font size calculation: {e}")
                    font_size -= 1
                    continue
                
                font_size -= 1
            
            return 8
        except Exception as e:
            logger.warning(f"Error calculating font size: {e}, using default 16")
            return 16

    def process_chat(self, text, posText, img):
        """
        Process the chat text and add it to the image.
        
        Features:
        - Dynamic font sizing
        - Text wrapping to fit textbox width
        - Clear original Japanese text with white background
        - Center-aligned text rendering
        - Graceful overflow handling

        Parameters:
            text (str): The text to be processed (Japanese).
            posText (tuple): The position of the textbox as [x1, y1, x2, y2].
            img (PIL.Image.Image): The image to add the processed text to.

        Returns:
            PIL.Image.Image: The image with the processed text added.
        """
        try:
            if not text or not text.strip():
                logger.warning("Empty text received, skipping processing")
                return img
            
            # Translate text to Vietnamese
            translated_text = self.translate_text(text)
            
            # Get textbox dimensions
            x1, y1, x2, y2 = posText
            box_width = x2 - x1
            box_height = y2 - y1
            padding = 10
            
            # Validate dimensions
            if box_width <= padding * 2 or box_height <= padding * 2:
                logger.warning(f"Textbox too small: {box_width}x{box_height}")
                return img
            
            # Step 1: Clear original text area with white background
            try:
                draw = ImageDraw.Draw(img)
                draw.rectangle([x1, y1, x2, y2], fill="white", outline=None)
                logger.info(f"Cleared textbox area: ({x1}, {y1}) to ({x2}, {y2})")
            except Exception as e:
                logger.warning(f"Error clearing text area: {e}")
            
            # Step 2: Calculate appropriate font size
            font_size = self.calculate_font_size(translated_text, box_width, box_height)
            
            # Step 3: Load font
            try:
                font = ImageFont.truetype(self.font_path, font_size)
                logger.info(f"Using font size: {font_size}pt")
            except Exception as e:
                logger.warning(f"Error loading font: {e}, using default font")
                font = ImageFont.load_default()
            
            # Step 4: Wrap text to fit width
            try:
                max_width = box_width - (padding * 2)
                lines = self.wrap_text(translated_text, font, max_width)
                logger.info(f"Text wrapped into {len(lines)} lines")
            except Exception as e:
                logger.error(f"Error wrapping text: {e}")
                lines = [translated_text]
            
            # Step 5: Calculate text positioning (vertical centering)
            try:
                bbox = font.getbbox("A")
                line_height = bbox[3] - bbox[1] + 3  # 3px spacing
                total_text_height = len(lines) * line_height
                
                # Center text vertically
                available_height = box_height - (padding * 2)
                start_y = y1 + padding + (available_height - total_text_height) // 2
                
                logger.info(f"Total text height: {total_text_height}px, positioning from y={start_y}")
            except Exception as e:
                logger.warning(f"Error calculating text positioning: {e}")
                start_y = y1 + padding
                line_height = font_size + 5
            
            # Step 6: Render text lines
            try:
                draw = ImageDraw.Draw(img)
                rendered_lines = 0
                
                for i, line in enumerate(lines):
                    y_pos = start_y + i * line_height
                    
                    # Check if line fits within textbox
                    if y_pos + font_size > y2 - padding:
                        logger.warning(f"Text overflow: Line {i+1} exceeds textbox height")
                        break
                    
                    # Center text horizontally
                    bbox = font.getbbox(line)
                    line_width = bbox[2] - bbox[0]
                    x_pos = x1 + padding + (max_width - line_width) // 2
                    
                    # Draw line
                    draw.text((x_pos, y_pos), line, fill=(0, 0, 0), font=font)
                    rendered_lines += 1
                
                logger.info(f"Successfully rendered {rendered_lines}/{len(lines)} lines of translated text")
                
            except Exception as e:
                logger.error(f"Error drawing text: {e}")
        
        except Exception as e:
            logger.error(f"Fatal error in process_chat: {e}")
            # Return original image if processing fails
        
        return img
    
    def __call__(self, img):
        """
        Main pipeline: detect -> OCR -> translate -> render
        
        Args:
            img (PIL.Image): Input manga page image
            
        Returns:
            PIL.Image: Processed image with translations
        """
        start_time = time.time()
        
        try:
            logger.info("Starting manga processing pipeline")
            self.processing_stats['total_images'] += 1
            
            # Detection
            try:
                textboxes = self.detect(img)
            except Exception as e:
                logger.error(f"Detection failed: {e}")
                return img
            
            if not textboxes:
                logger.info("No textboxes detected")
                return img
            
            self.processing_stats['total_textboxes'] += len(textboxes)
            
            # Process each textbox
            processed_count = 0
            for idx, textbox in enumerate(textboxes):
                try:
                    logger.info(f"Processing textbox {idx+1}/{len(textboxes)}")
                    
                    # Crop image
                    try:
                        bubble_chat = img.crop((textbox[0], textbox[1], textbox[2], textbox[3]))
                    except Exception as e:
                        logger.error(f"Error cropping textbox {idx}: {e}")
                        continue
                    
                    # OCR
                    try:
                        text = self.recognizer(bubble_chat)
                        logger.info(f"OCR result: {text[:50]}...")
                    except Exception as e:
                        logger.error(f"OCR error for textbox {idx}: {e}")
                        continue
                    
                    # Process and render
                    try:
                        img = self.process_chat(text, textbox, img)
                        processed_count += 1
                    except Exception as e:
                        logger.error(f"Error processing chat {idx}: {e}")
                        continue
                
                except Exception as e:
                    logger.error(f"Unexpected error processing textbox {idx}: {e}")
                    continue
            
            elapsed_time = time.time() - start_time
            self.processing_stats['processed_images'] += 1
            self.processing_stats['total_time'] += elapsed_time
            
            logger.info(f"Pipeline completed: {processed_count}/{len(textboxes)} textboxes processed in {elapsed_time:.2f}s")
            return img
        
        except Exception as e:
            logger.error(f"Fatal error in pipeline: {e}")
            return img

    
if __name__=='__main__':    
    try:
        reader = Manga_Reader()
        img = Image.open("test/jjk4.png")
        img = reader(img)
        img.show()
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
