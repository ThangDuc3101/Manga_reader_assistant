import streamlit as st
from PIL import Image
from reader import Manga_Reader
import os

def app():
    """
    This function is the main entry point of the MANGA READER application. It displays a title and author information, and allows the user to upload multiple image files. For each uploaded image, it processes the image by opening it, applying the Manga_Reader class to convert the text in the image to Vietnamese, and then displays the result. The processed image is also saved in the 'translated' folder with a modified file name. This function does not take any parameters and does not return any values.
    """
       
    st.title("MANGA READER")
    st.text("Author: ThangBui")
    st.text("Framework: Ultralytics, OCR, Streamlit")
    
    upload_images = st.sidebar.file_uploader("Upload multiple files",accept_multiple_files=True)
    reader = Manga_Reader()

    for upload_image in upload_images:   
        # Process the input image
        image = Image.open(upload_image)            
        imageTrans = reader(image) 
        
        # Display the result
        st.balloons()   
        st.image(imageTrans)
                
        # Save an PIL image
        image_name = upload_image.name.split('.')[0] + '.png'
        imageTrans.save(os.path.join('translated', image_name))
        
        st.info("This file was saved in translated folder") 