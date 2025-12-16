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

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

class Manga_Reader:
    def __init__(self, detector=None, use_roboflow=True):
        """
        Initialize Manga Reader.
        
        Args:
            detector: Path to local YOLO model (if use_roboflow=False)
            use_roboflow: If True, use Roboflow API for detection
        """
        self.use_roboflow = use_roboflow
        
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
            self.translator = GoogleTranslator(source='ja', target='vi')
            logger.info("Google Translator initialized successfully")
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
            while font_size > 10:
                try:
                    font = ImageFont.truetype(self.font_path, font_size)
                    bbox = font.getbbox(text)
                    text_width = bbox[2] - bbox[0]
                    
                    if text_width <= box_width * 0.9:
                        return font_size
                except Exception:
                    font_size -= 2
                    continue
                
                font_size -= 2
            
            return 10
        except Exception as e:
            logger.warning(f"Error calculating font size: {e}, using default 20")
            return 20

    def process_chat(self, text, posText, img):
        """
        Process the chat text and add it to the image.

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
            
            draw = ImageDraw.Draw(img)
            
            # Calculate dimensions
            x1, y1, x2, y2 = posText
            box_width = x2 - x1
            box_height = y2 - y1
            
            # Clear original text by filling with white
            try:
                draw.rectangle([x1, y1, x2, y2], fill="white")
                logger.info("Cleared original text area")
            except Exception as e:
                logger.warning(f"Error clearing text area: {e}")
            
            # Calculate appropriate font size
            font_size = self.calculate_font_size(translated_text, box_width, box_height)
            
            try:
                font = ImageFont.truetype(self.font_path, font_size)
            except Exception as e:
                logger.warning(f"Error loading font: {e}, using default font")
                font = ImageFont.load_default()
            
            # Split text into lines
            chat = translated_text.split(" ")
            content = []
            for i in range(len(chat)):
                if i % 2 == 1:
                    content.append(chat[i-1] + " " + chat[i])
                
                if (i == len(chat) - 1) and (i % 2 == 0):
                    content.append(chat[i])
                    break
            
            # Draw text
            try:
                line_height = font_size + 5
                for i, line in enumerate(content):
                    y_pos = y1 + i * line_height
                    if y_pos + font_size > y2:
                        logger.warning("Text overflow in textbox")
                        break
                    draw.text((x1 + 5, y_pos), line, (255, 0, 0), font=font)
                
                logger.info(f"Rendered {len(content)} lines of translated text")
            except Exception as e:
                logger.error(f"Error drawing text: {e}")
        
        except Exception as e:
            logger.error(f"Error in process_chat: {e}")
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
        try:
            logger.info("Starting manga processing pipeline")
            
            # Detection
            try:
                textboxes = self.detect(img)
            except Exception as e:
                logger.error(f"Detection failed: {e}")
                return img
            
            if not textboxes:
                logger.info("No textboxes detected")
                return img
            
            # Process each textbox
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
                    except Exception as e:
                        logger.error(f"Error processing chat {idx}: {e}")
                        continue
                
                except Exception as e:
                    logger.error(f"Unexpected error processing textbox {idx}: {e}")
                    continue
            
            logger.info("Pipeline completed successfully")
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
