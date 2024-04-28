import streamlit as st
from streamlit_option_menu import option_menu
import about,assistant,readOnly
class Manga_Reader_App:
    def __init__(self) -> None:
        self.app = []
    def add_app(self,title,func):
        self.app.append({
            "title":title,
            "function":func	
        })
    def run():
        with st.sidebar:
            app = option_menu(
                menu_title = "Main Menu",
                options = ["Assistant", "Read Only", "About"],
                icons = ["chat-text", "book", "info-circle-fill"],
                menu_icon = "bounding-box",
                default_index = 0
            )
            
        if app == "Assistant":
            assistant.app()
        if app == "Read Only":
            readOnly.app()
        if app == "About":
            about.app()
    
    run()        