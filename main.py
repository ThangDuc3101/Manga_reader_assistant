import streamlit as st
from streamlit_option_menu import option_menu
import about
import assistant
import readOnly
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """
    Main entry point of Manga Reader Assistant application.
    Manages sidebar menu and routes to different pages.
    """
    try:
        # Configure Streamlit page
        st.set_page_config(
            page_title="Manga Reader Assistant",
            page_icon="📖",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Sidebar menu
        with st.sidebar:
            app = option_menu(
                menu_title="Main Menu",
                options=["Assistant", "Read Only", "About"],
                icons=["chat-text", "book", "info-circle-fill"],
                menu_icon="bounding-box",
                default_index=0
            )
        
        # Route to selected page
        try:
            if app == "Assistant":
                assistant.app()
            elif app == "Read Only":
                readOnly.app()
            elif app == "About":
                about.app()
        except Exception as e:
            logger.error(f"Error in app routing: {e}")
            st.error(f"An error occurred in {app} page: {str(e)}")
    
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        st.error("Application error. Please refresh the page.")

if __name__ == "__main__":
    main()
