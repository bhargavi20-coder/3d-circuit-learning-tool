import streamlit as st
import streamlit.components.v1 as components
import os

# Set page configuration for full-width layout
st.set_page_config(
    page_title="Learn Arduino - 3D Interactive Workbench",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load the local HTML visualizer file
html_file_path = os.path.join(os.path.dirname(__file__), "visualizer.html")

if os.path.exists(html_file_path):
    with open(html_file_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # Render the interactive 3D application inside Streamlit
    components.html(html_content, height=850, scrolling=False)
else:
    st.error("Error: 'visualizer.html' not found in your project folder! Please make sure both app.py and visualizer.html are in C:\\Users\\bharg\\OneDrive\\Desktop\\circuit_3d_app.")
