import streamlit as st
import importlib

st.set_page_config(
        page_title="City Map Dashboard",
        layout="wide",  # Options: 'centered' or 'wide'
        initial_sidebar_state="expanded"  # Optional: 'expanded', 'collapsed'
    )

st.title("Home")
