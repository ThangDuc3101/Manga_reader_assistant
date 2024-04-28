import streamlit as st
from PIL import Image

def app():
    """
    This function is the main entry point of the MANGA READER application. It displays a title and author information, and allows the user to upload multiple image files. Show all the images that you saved in the 'translated' folder. This function does not take any parameters and does not return any values.
    """
        
    st.title("MANGA READER")
    st.text("Author: ThangBui")
    st.text("Framework: Ultralytics, OCR, Streamlit")
    
    upload_images = st.sidebar.file_uploader("Upload multiple files",accept_multiple_files=True)
    
    st.write("In this tab, you can read translated manga that you saved")
    for upload_image in upload_images:
        image = Image.open(upload_image)
        st.image(image)