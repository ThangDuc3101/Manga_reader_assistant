import streamlit as st
from streamlit_option_menu import option_menu
import about, assistant, readOnly


def main():
    """Main entry point for the Manga Reader application."""
    with st.sidebar:
        selected_page = option_menu(
            menu_title="Main Menu",
            options=["Assistant", "Read Only", "About"],
            icons=["chat-text", "book", "info-circle-fill"],
            menu_icon="bounding-box",
            default_index=0
        )
    
    if selected_page == "Assistant":
        assistant.app()
    elif selected_page == "Read Only":
        readOnly.app()
    elif selected_page == "About":
        about.app()


if __name__ == "__main__":
    main()        