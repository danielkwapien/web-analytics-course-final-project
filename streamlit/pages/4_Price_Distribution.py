import streamlit as st
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# Define the page function
def app():
    st.title("Average Price Distributions by State (Histogram)")

    # Load data
    try:
        # Replace 'data/events.csv' with the path to your actual data file
        events_df = pd.read_csv("data/events.csv")
    except FileNotFoundError:
        st.error("Data file not found. Please ensure 'data/events.csv' is available.")
        return

    # Ensure required columns are present
    if all(col in events_df.columns for col in ['venue_state', 'venue_city', 'average_price']):
        state_options = events_df['venue_state'].unique()
        selected_state = st.selectbox("Select State", options=state_options, index=0)

        view_option = st.radio("Select View", ["City-level Histograms", "State-wide Histogram"], index=0)

        filtered_data = events_df[events_df['venue_state'] == selected_state]

        if view_option == "City-level Histograms":
            cities = filtered_data['venue_city'].unique()

            subplot_titles = [f"{city} Average Price Distribution" for city in cities[:10]]  # Limit to 10 cities

            fig = make_subplots(
                rows=len(cities[:10]),
                cols=1,
                subplot_titles=subplot_titles,
                vertical_spacing=0.05
            )

            for i, city in enumerate(cities[:10], start=1):  # Limit to the first 10 cities
                city_data = filtered_data[filtered_data['venue_city'] == city]

                fig.add_trace(
                    go.Histogram(
                        x=city_data['average_price'],
                        name=f'{city} Average Price',
                        marker_color='blue',
                        opacity=0.7,
                    ),
                    row=i,
                    col=1
                )

            # Update layout
            fig.update_layout(
                height=300 * len(cities[:10]),  # Adjust height based on number of cities
                width=800,
                title_text=f"City-level Average Price Distributions in {selected_state} (Histogram)",
                showlegend=False
            )

            # Update axes titles for each subplot
            for i in range(1, len(cities[:10]) + 1):
                fig.update_xaxes(title_text="Average Price", row=i, col=1)
                fig.update_yaxes(title_text="Frequency", row=i, col=1)

        elif view_option == "State-wide Histogram":
            # Create a single histogram for the entire state
            fig = go.Figure()

            fig.add_trace(
                go.Histogram(
                    x=filtered_data['average_price'],
                    name=f'{selected_state} Average Price',
                    marker_color='green',
                    opacity=0.7
                )
            )

            # Update layout
            fig.update_layout(
                height=600,
                width=800,
                title_text=f"State-wide Average Price Distribution in {selected_state} (Histogram)",
                xaxis_title="Average Price",
                yaxis_title="Frequency",
                showlegend=False
            )

        # Display the plot in Streamlit
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error(
            "Data file is missing required columns: 'venue_state', 'venue_city', 'average_price'."
        )

# Call the function for the multi-page app
app()
