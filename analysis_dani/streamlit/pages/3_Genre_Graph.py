import streamlit as st
import plotly.express as px
import pandas as pd

# Define the page function
def app():
    st.title("Genre Graph: Price Ranges and Sub-Genres")

    # Load data
    try:
        # Replace 'data/prices_by_genre.csv' with the path to your actual data file
        prices_by_genre = pd.read_csv("data/prices_by_genre.csv")
    except FileNotFoundError:
        st.error("Data file not found. Please ensure 'data/prices_by_genre.csv' is available.")
        return

    # Ensure required columns are present
    if all(col in prices_by_genre.columns for col in ['segment_name', 'genre_name', 'sub_genre_name', 'average_price', 'count']):
        # Add filters for segments and toggles for genres/sub-genres
        segment_options = prices_by_genre['segment_name'].unique()
        selected_segment = st.selectbox("Select Segment", options=segment_options, index=0)

        toggle_view = st.radio(
            "Choose View:",
            options=["Genres", "Sub-genres"],
            index=0
        )

        # Filter the dataset by selected segment
        filtered_data = prices_by_genre[prices_by_genre['segment_name'] == selected_segment]

        # Update the view based on the toggle
        if toggle_view == "Genres":
            x_axis = "genre_name"
            title = f"Bubble Plot of Genres for {selected_segment}"
            aggregated_data = filtered_data.groupby("genre_name").agg(
                average_price=('average_price', 'mean'),  # Mean price for the genre
                count=('count', 'sum')  # Total count for the genre
            ).reset_index()
        elif toggle_view == "Sub-genres":
            x_axis = "sub_genre_name"
            title = f"Bubble Plot of Sub-genres for {selected_segment}"

            # Add a new column combining genre and sub-genre
            filtered_data['genre_subgenre'] = (
                filtered_data['genre_name'] + " - " + filtered_data['sub_genre_name']
            )

            aggregated_data = filtered_data

        # Use "genre_subgenre" as the y-axis for sub-genres
        x_axis = "genre_subgenre" if toggle_view == "Sub-genres" else "genre_name"

        # Create the scatter (bubble) plot
        fig = px.scatter(
            aggregated_data,
            x=x_axis,
            y="average_price",
            size="count",
            size_max=50,
            hover_name=x_axis,
            title=title,
            labels={
                "average_price": "Average Price",
                "count": "Number of Events",
                x_axis: "Category"
            }
        )

        # Update layout for better visuals
        fig.update_layout(
            xaxis_title="Category",
            yaxis_title="Category (Genre-Subgenre)" if toggle_view == "Sub-genres" else "Average Price",
            xaxis_tickangle=45,
            height=600,
            width=1000
        )

        # Display the plot in Streamlit
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error(
            "Data file is missing required columns: 'segment_name', 'genre_name', 'sub_genre_name', 'average_price', 'count'."
        )

# Call the function for the multi-page app
app()
