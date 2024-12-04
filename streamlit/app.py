import streamlit as st
import importlib

# Sidebar Navigation
st.sidebar.title("Visualization Dashboard")
selected_tab = st.sidebar.radio(
    "Choose a visualization",
    ["Home", "City Map", "Genre Graph", "State Map"]
)

# Dynamically import and run the selected tab
if selected_tab == "Home":
    from pages import home
    importlib.reload(home)
    home.show()

elif selected_tab == "City Map":
    from pages import city_map
    importlib.reload(city_map)
    city_map.show()

elif selected_tab == "Genre Graph":
    from pages import genre_graph
    importlib.reload(genre_graph)
    genre_graph.show()

elif selected_tab == "State Map":
    from pages import state_map
    importlib.reload(state_map)
    state_map.show()
