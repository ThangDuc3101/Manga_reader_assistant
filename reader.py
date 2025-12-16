from ultralytics import YOLO
from googletrans import Translator
from PIL import Image, ImageDraw, ImageFont
from manga_ocr import MangaOcr
from roboflow import Roboflow
from dotenv import load_dotenv
import os
import numpy as np

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
        
        if use_roboflow:
            # Roboflow API setup - sử dụng model comic-text-bubble-detection
            api_key = os.getenv("ROBOFLOW_API_KEY", "")
            if not api_key:
                raise ValueError("ROBOFLOW_API_KEY not found. Please set it in .env file")
            rf = Roboflow(api_key=api_key)
            project = rf.workspace().project("comic-text-bubble-detection-yfsxo")
            self.model = project.version(1).model
        else:
            # Local YOLO model
            if detector is None:
                detector = "yolov8_manga.pt"
            self.model = YOLO(detector)
        
        self.recognizer = MangaOcr()        # Manga-OCR
        self.translator = Translator()      # Translator
        
        # Font path - sử dụng đường dẫn tuyệt đối
        self.font_path = os.path.join(os.path.dirname(__file__), "font", "arial.ttf")
        
    def detect(self, frame):
        """
        Detects textboxes in a frame using the YOLO model. 

        Parameters:
            frame: the input frame to detect textboxes (PIL Image).

        Returns:
            A list of textboxes where each box is represented as [x1, y1, x2, y2].
        """
        textboxes = []
        
        if self.use_roboflow:
            # Roboflow API - cần lưu ảnh tạm để predict
            temp_path = "temp_frame.jpg"
            frame.save(temp_path)
            results = self.model.predict(temp_path, confidence=40).json()
            os.remove(temp_path)
            
            for prediction in results.get("predictions", []):
                x_center = prediction["x"]
                y_center = prediction["y"]
                width = prediction["width"]
                height = prediction["height"]
                
                x1 = int(x_center - width / 2)
                y1 = int(y_center - height / 2)
                x2 = int(x_center + width / 2)
                y2 = int(y_center + height / 2)
                textboxes.append([x1, y1, x2, y2])
        else:
            # Local YOLO model
            results = self.model(frame)
            box = results[0].boxes
            for b in box:
                x1, y1, x2, y2 = b.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                textboxes.append([x1, y1, x2, y2])
        
        return textboxes   
    def process_chat(self,text,posText,img):
        """
        Process the chat text and add it to the image.

        Parameters:
            text (str): The text to be processed.
            posText (tuple): The position of the text on the image.
            img (PIL.Image.Image): The image to add the processed text to.

        Returns:
            PIL.Image.Image: The image with the processed text added.
        """
        # Translated text to Vietnamese
        translated = self.translator.translate(text,src="ja",dest="vi")        
        
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(self.font_path, 40)
        
        chat = translated.text.split(" ")
        content=[]        
        for i in range(len(chat)):
            if i%2==1:
                content.append(chat[i-1]+" "+chat[i])
            
            if (i==len(chat)-1) & (i%2==0):
                content.append(chat[i])
                break
                
        for i in range(len(content)):
            draw.text((posText[0],posText[1]+i*40),content[i],(255,0,0),font=font)
        return img
    
    def __call__(self, img):
        
        # img = Image.open(path)           
        textboxes = self.detect(img)
    
        for textbox in textboxes:
            # crop image with PIL
            bubble_chat = img.crop((textbox[0],textbox[1],textbox[2],textbox[3]))   

            text = self.recognizer(bubble_chat)         

            img = self.process_chat(text,textbox,img)
        return img
    
       
if __name__=='__main__':    
    reader = Manga_Reader()
    img = Image.open("test/jjk4.png")
    img = reader(img)
    img.show()
           

    
          
      
