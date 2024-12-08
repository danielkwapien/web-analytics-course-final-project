import streamlit as st
import plotly.graph_objects as go
import pandas as pd


# Define the page as a function to encapsulate the logic
def app():
    st.title("City Map: Average Prices by Venue")

    # Load data
    try:
        # Replace 'data/prices_by_city.csv' with the path to your actual data file
        average_prices_df = pd.read_csv("data/prices_by_city.csv")
    except FileNotFoundError:
        st.error("Data file not found. Please ensure 'data/prices_by_city.csv' is available.")
        return

    # Ensure required columns are present
    if all(col in average_prices_df.columns for col in
           ['venue_latitude', 'venue_longitude', 'average_price', 'venue_city']):
        # Create the map
        fig = go.Figure()

        fig.add_trace(go.Scattermapbox(
            lat=average_prices_df['venue_latitude'],
            lon=average_prices_df['venue_longitude'],
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=average_prices_df['average_price'],  # Scale size
                color=average_prices_df['average_price'],
                showscale=True,  # Display colorbar
                sizemode='area',
                colorbar=dict(title="Avg Price")
            ),
            text=average_prices_df.apply(lambda row: f"{row['venue_city']}<br>Avg Price: {row['average_price']:.2f}",
                                         axis=1),
            name="Average Price"
        ))

        # Update layout to mimic the px.scatter_mapbox style
        fig.update_layout(
            mapbox=dict(
                style="carto-positron",
                zoom=3,
                center={
                    "lat": average_prices_df['venue_latitude'].mean(),
                    "lon": average_prices_df['venue_longitude'].mean()
                }
            ),
            margin={"r": 0, "t": 40, "l": 0, "b": 0},
            title="Bubble Map of Average Prices by Venue in the USA",
            height=600,
            width=1200
        )

        # Display the map in Streamlit
        st.plotly_chart(fig, use_container_width=False, theme=None)
    else:
        st.error(
            "Data file is missing required columns: 'venue_latitude', 'venue_longitude', 'average_price', 'venue_city'.")

    st.text('We can clearly shee that the higher average prices are in Santa Clara and Inglewood. That is because in both cities we have an NFL stadium, which has higher prices than other venues.'
            'Additionally in Inglewood, since it is the SoFi stadium, there are also big concerts hosted')


# Call the function for the multi-page app
app()