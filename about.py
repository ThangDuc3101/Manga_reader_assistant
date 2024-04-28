import streamlit as st
from PIL import Image
def app():  
    """
    This function is the main entry point of the MANGA READER application. It displays a title and author information, and provides information about the project. 
    """
        
    st.title("MANGA READER")
    st.text("Author: ThangBui")
    st.text("Framework: Ultralytics, OCR, Streamlit")
    
    st.header("Some infomation of this project")
    st.write("This project was created to read Japanese manga in Vietnamese. So, I used YOLO to detect textbox after that use OCR to text recognize then translate them into Vietnamese.")
        
    st.header("Model")
    model = Image.open("img/pruning_model.png")
    st.image(model)
    st.write("I used YOLOv8 with size l. But it is very large so I pruns 2 heads of it.")
    
    st.header("OCR")
    st.write("I used Manga-OCR lib. You can visit its source code in here: https://github.com/kha-white/manga-ocr")
    
    st.header("Translate")
    st.write("I used Google Translate lib.")