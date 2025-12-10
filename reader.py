import logging
from ultralytics import YOLO
from googletrans import Translator
from PIL import Image, ImageDraw, ImageFont
from manga_ocr import MangaOcr

logger = logging.getLogger(__name__)


class Manga_Reader:
    """Manga reader that detects text, recognizes it, and translates to Vietnamese."""
    
    FONT_SIZE = 40
    TEXT_COLOR = (255, 0, 0)  # Red in BGR
    MAX_TEXT_LENGTH = 500
    
    def __init__(self, detector="yolov8_manga.pt"):
        """
        Initialize Manga Reader with YOLO detector, OCR, and translator.
        
        Parameters:
            detector (str): Path to YOLO model weights file.
        """
        try:
            self.model = YOLO(detector)
            self.recognizer = MangaOcr()
            self.translator = Translator()
            logger.info("Manga_Reader initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Manga_Reader: {e}")
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
           

    
          
      
