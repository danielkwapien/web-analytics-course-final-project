import streamlit as st

st.set_page_config(
        page_title="Marketing Analysis for Events in USA",
        page_icon="🌆",
        layout="wide",  # Options: 'centered' or 'wide'
        initial_sidebar_state="expanded"  # Optional: 'expanded', 'collapsed'
    )

# App title and introduction
st.title("Marketing Analysis for Events in USA")
st.markdown(
    """
    ## Objective

    This dashboard provides an analysis to help optimize event marketing strategies. 
    Users can explore insights by **location** (state or city) or by **event genre** to make data-driven decisions.

    ### Key Features:

    - **State/City Analysis**:
      - Price distribution by genre and venue
      - Popular event types in the location
      - Relationships between venues and hosted genres
      - Key artists and attractions in the location

    - **Genre Analysis**:
      - Price trends for the genre across cities and states
      - Genre popularity in different locations
      - Venues specialized or diverse in the selected genre
      - Artists associated with the genre and their pricing trends

    Navigate through the tabs for specific insights.
    """
)

# pg = st.navigation([st.Page("pages/page_genre.py"), st.Page("pages/page_city.py")])
# pg.run()