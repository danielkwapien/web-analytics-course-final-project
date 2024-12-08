import streamlit as st
import plotly.express as px
import pandas as pd

# Define the page function
def app():
    st.title("State Map: Average Prices by State")

    # Load data
    try:
        # Replace 'data/prices_by_state.csv' with the path to your actual data file
        average_prices_df = pd.read_csv("data/prices_by_state.csv")
    except FileNotFoundError:
        st.error("Data file not found. Please ensure 'data/prices_by_state.csv' is available.")
        return

    # Ensure required columns are present
    if all(col in average_prices_df.columns for col in ['venue_state_code', 'average_price']):
        # Create the choropleth map
        fig = px.choropleth(
            average_prices_df,
            locations="venue_state_code",              # State abbreviations
            locationmode="USA-states",                 # USA states
            color="average_price",                     # Column to use for coloring
            scope="usa",                               # Focus on the USA
            title="Choropleth Map of Average Prices by State"
        )

        # Update layout for better visuals
        fig.update_layout(
            geo=dict(
                lakecolor="rgb(255, 255, 255)"  # Optional: make lakes white
            ),
            height=800,
            width=1000
        )

        # Display the map in Streamlit
        st.plotly_chart(fig, use_container_width=True, theme=None)
    else:
        st.error("Data file is missing required columns: 'venue_state_code', 'average_price'.")

# Call the function for the multi-page app
app()
