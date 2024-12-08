from calendar import day_abbr

import streamlit as st
import importlib

from utils.utils import *
from modules.attractions_module.attractions_analysis import *
from modules.popularity_module.genre_popularity_events_map import *
from streamlit_folium import st_folium
from data import *
from streamlit_plotly_events import plotly_events
import plotly.express as px


st.title("Genre Events Analysis")

df = load_data()

# -------------------------------------------------------------------------------------------------------
#                                                STATE MAP
# -------------------------------------------------------------------------------------------------------

# Get subset necessary to create popularity event map
df['average_price'] = (df['min_price'] + df['max_price']) / 2
df = df[df['genre_name'] != 'Undefined']
data_subset = df[['event_name', 'venue_state', 'venue_city', 'segment_name', 'genre_name', 'sub_genre_name', 'start_date', 'venue_latitude', 'venue_longitude', 'min_price', 'max_price', 'average_price']]

# Aggregate data for event counts (per segment)
data_segment_eventcount = data_subset.groupby(['venue_state', 'venue_city', 'segment_name']).agg(event_count=('event_name', 'count')).reset_index()

# Aggregate data for event counts (per segment and genre)
data_segment_classification_eventcount = data_subset.groupby(['venue_state', 'venue_city', 'segment_name', 'genre_name']).agg(event_count=('event_name', 'count')).reset_index()
data_segment_classification_eventcount = data_segment_classification_eventcount.sort_values(by=['event_count'], ascending=False)
data_segment_price = data_subset.groupby(['venue_state', 'segment_name', 'genre_name', 'sub_genre_name']).agg(average_price=('average_price', 'mean'), count=('max_price', 'count')).reset_index()
data_segment_price = data_segment_price[data_segment_price['genre_name'] != 'Undefined']

data_state_price = pd.read_csv("data/prices_by_state.csv")
data_state_price = data_state_price[data_state_price['segment_name'] != 'Undefined']

# Prepare data for the map (count the number of events happening in each state)
state_counts = (
    data_segment_classification_eventcount.groupby("venue_state")["event_count"]
    .sum()
    .reset_index()
    .rename(columns={"event_count": "total_events"})
)

# Prepare data for the map (count the number of events happening in each state)
state_segment_counts = (
    data_segment_classification_eventcount.groupby(["venue_state", "segment_name"])["event_count"]
    .sum()
    .reset_index()
    .rename(columns={"event_count": "total_events"})
)

# Count the number of unique classifications (genres) happening in each state for each segment and genre
state_segment_genre_counts = (
    data_segment_classification_eventcount.groupby(["venue_state", "segment_name", "genre_name"])["event_count"]
    .sum()
    .reset_index()
    .rename(columns={"event_count": "total_events"})
)

# Load GeoJSON data for US states
with open('data/georef-united-states-of-america-state.geojson', 'r') as f:
    geojson_data = json.load(f)

# Make some changes over the geojson so that the states are not inside a list
for i in range(len(geojson_data["features"])):
  feature = geojson_data["features"][i]
  geojson_data["features"][i]["properties"]["ste_name"] = feature['properties']['ste_name'][0]

segments = df.groupby(['segment_name'])['genre_name'].apply(set).to_dict()

# Allow the user to select a segment dynamically
selected_segment = st.selectbox("Select a Segment", list(segments.keys()))


# Offer the user to select a subgenre or choose "All"
if selected_segment:
    subgenres = ["All"] + sorted(segments[selected_segment])  # Add "All" as the first option
    selected_genre = st.selectbox("Select a specific Genre", subgenres)

price_tab, popularity_tab, attractions_tab = st.tabs(['Price Analysis', 'Genre Popularity Analysis', 'Top Attractions by Genre'])

with price_tab:
    # Display a section for price analysis
    st.markdown("## Price Analysis for Selected Segment")

    if all(col in data_segment_price.columns for col in ['venue_state', 'segment_name', 'genre_name', 'sub_genre_name', 'average_price', 'count']):
        # Get unique segment options for filtering

        state_options = ["All States"] + list(data_segment_price['venue_state'].unique())
        selected_state = st.selectbox("Select a State", options=state_options, index=0)

        # Allow the user to toggle between viewing genres and sub-genres
        toggle_view = st.radio(
            "Choose View:",
            options=["Genres", "Sub-genres"],
            index=0
        )

        # Filter the dataset based on the selected segment
        filtered_data = data_segment_price[data_segment_price['segment_name'] == selected_segment]
        if selected_state != "All States":
            filtered_data = filtered_data[filtered_data['venue_state'] == selected_state]

        # Handle data aggregation and title setup based on the view
        if toggle_view == "Genres":
            x_axis = "genre_name"
            title = f"Bubble Plot of Genres for {selected_segment} in {selected_state}"
            aggregated_data = filtered_data.groupby("genre_name").agg(
                average_price=('average_price', 'mean'),  # Calculate mean price per genre
                count=('count', 'sum')  # Sum the counts for each genre
            ).reset_index()
        elif toggle_view == "Sub-genres":
            # Combine genre and sub-genre into a single column for unique identification
            filtered_data['genre_subgenre'] = (
                    filtered_data['genre_name'] + " - " + filtered_data['sub_genre_name']
            )
            x_axis = "genre_subgenre"
            title = f"Bubble Plot of Sub-genres for {selected_segment} in {selected_state}"
            aggregated_data = filtered_data.groupby("genre_subgenre").agg(
                average_price=('average_price', 'mean'),
                count=('count', 'sum')
            ).reset_index()

        # Create the scatter (bubble) plot
        fig = px.scatter(
            aggregated_data,
            x=x_axis,  # Dynamic x-axis based on the view
            y="average_price",  # Display average price on the y-axis
            size="count",  # Bubble size based on event count
            size_max=50,  # Limit maximum bubble size
            hover_name=x_axis,  # Show category names on hover
            title=title,  # Dynamic title for the chart
            labels={
                "average_price": "Average Price",  # Y-axis label
                "count": "Number of Events",  # Bubble size label
                x_axis: "Category"  # X-axis label
            }
        )

        # Update layout for better visuals and usability
        fig.update_layout(
            xaxis_title="Category",  # Title for x-axis
            yaxis_title="Average Price",
            # Dynamic y-axis title
            xaxis_tickangle=45,  # Rotate x-axis labels for better readability
            height=600,  # Chart height
            width=1000  # Chart width
        )

        # Render the plot in Streamlit
        st.plotly_chart(fig, use_container_width=True)

        choropleth_data = data_state_price[data_state_price["segment_name"] == selected_segment]
        if selected_genre != "All":
            choropleth_data = choropleth_data[choropleth_data["genre_name"] == selected_genre]
        choropleth_data = choropleth_data.groupby("venue_state_code").agg(average_price=("average_price", "mean")).reset_index()

        if not choropleth_data.empty:
            fig_choropleth = px.choropleth(
                choropleth_data,
                locations="venue_state_code",  # State abbreviations
                locationmode="USA-states",  # USA states
                color="average_price",  # Column to use for coloring
                scope="usa",  # Focus on the USA
                title=f"Choropleth Map of Average Prices by State for {selected_segment}"
            )

            # Update layout for better visuals
            fig_choropleth.update_layout(
                geo=dict(
                    lakecolor="rgb(255, 255, 255)"  # Optional: make lakes white
                ),
                height=800,
                width=1000
            )

            # Display the map in Streamlit
            st.plotly_chart(fig_choropleth, use_container_width=True)

    else:
        # Display an error if required columns are missing from the dataset
        st.error(
            "Data file is missing required columns: 'segment_name', 'genre_name', 'sub_genre_name', 'average_price', 'count'."
        )

with popularity_tab:
    # TODO add popularity analysis here
    st.markdown(f"## Popularity Analysis for {selected_segment}")

    # Filter data by segment and genre
    if selected_segment:
        segment_data = state_segment_counts[state_segment_counts["segment_name"] == selected_segment]

        if selected_genre and selected_genre != "All":
            filtered_data = state_segment_genre_counts[
                (state_segment_genre_counts["segment_name"] == selected_segment) &
                (state_segment_genre_counts["genre_name"] == selected_genre)
            ]
        else:
            filtered_data = segment_data
    else:
        filtered_data = state_counts  # Default to overall state counts
    
    # Display the top 10 states table
    if selected_genre and selected_genre != "All":
        st.markdown(f"#### Top 10 States for {selected_segment} - {selected_genre}")
    else:
        st.markdown(f"#### Top 10 States for {selected_segment}")
    
    with st.expander('Top 10 States', expanded=True):

        # Sort the filtered data to get the top 10 states
        top_10_states = (
            filtered_data.nlargest(10, "total_events")
            .rename(columns={"total_events": "Event Count", "venue_state": "State"})
            [["State", "Event Count"]]
            .reset_index(drop=True)
        )
        top_10_states.index += 1

        st.table(top_10_states)
    
    if selected_genre and selected_genre != "All":
        st.markdown(f"#### {selected_segment} - {selected_genre} Events Across All States")
    else:
        st.markdown(f"#### {selected_segment} Events Across All States")

    with st.expander('Events Across All States', expanded=True):
        # Create the map
        event_map = create_map_event_popularity_state(filtered_data, geojson_data)

        # Display the map in Streamlit
        st_data = st_folium(event_map, width=700, height=600)
    
    # Aggregate data by segment_name for fig1
    aggregated_segment_counts = (
        state_segment_counts.groupby("segment_name", as_index=False)["total_events"]
        .sum()
    )

    # General Bar Charts (Default State)
    fig1 = px.bar(
        aggregated_segment_counts,
        x="segment_name",
        y="total_events",
        color="segment_name",
        title="Overall Event Count per Segment (All States)",
        labels={"segment_name": "Segment", "total_events": "Event Count"},
        color_discrete_sequence=px.colors.qualitative.Set2,
    )

    # Aggregate data by genre_name for fig2
    aggregated_genre_counts = (
        state_segment_genre_counts.groupby("genre_name", as_index=False)["total_events"]
        .sum()
    )

    fig2 = px.bar(
        aggregated_genre_counts,
        x="genre_name",
        y="total_events",
        color="genre_name",
        title="Overall Event Count per Genre (All States)",
        labels={"genre_name": "Genre", "total_events": "Event Count"},
        color_discrete_sequence=px.colors.qualitative.Set2,
    )

    # Add reset button
    if st.button("Reset Charts"):
        # Reset charts to default states
        fig1 = px.bar(
                aggregated_segment_counts,
                x="segment_name",
                y="total_events",
                color="segment_name",
                title="Overall Event Count per Segment (All States)",
                labels={"segment_name": "Segment", "total_events": "Event Count"},
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
        
        fig2 = px.bar(
                aggregated_genre_counts,
                x="genre_name",
                y="total_events",
                color="genre_name",
                title="Overall Event Count per Genre (All States)",
                labels={"genre_name": "Genre", "total_events": "Event Count"},
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
        # Re-render the charts to reset to their default values
        with st.expander('Select a State for More Detail', expanded=True):
            st.plotly_chart(fig1, use_container_width=True)
        with st.expander('Select a Segment for More Detail', expanded=True):
            st.plotly_chart(fig2, use_container_width=True)

    else:
        # Proceed with normal flow if reset is not clicked

        st.markdown(f"#### Information Across States")

        # Handle state selection on the map
        clicked_state = None
        if st_data and st_data.get("last_active_drawing"):
            clicked_state = st_data["last_active_drawing"]["properties"].get("ste_name")
            st.write(f"**Selected State:** {clicked_state}")

        # Update the first chart if a state is selected
        if clicked_state:
            filtered_state_data = state_segment_counts[state_segment_counts['venue_state'] == clicked_state]
            if not filtered_state_data.empty:
                fig1 = px.bar(
                    filtered_state_data,
                    x="segment_name",
                    y="total_events",
                    color="segment_name",
                    title=f"Overall Event Count by Segment in {clicked_state}",
                    labels={"segment_name": "Segment", "total_events": "Event Count"},
                    color_discrete_sequence=px.colors.qualitative.Light24,
                )

        # Expander for the first bar chart
        with st.expander('Select a State for More Detail', expanded=True):
            fig1.update_layout(
                title=f"Event Count per Segment ({clicked_state if clicked_state else 'All States'})",  # Dynamic title update
                title_font=dict(size=14, family="Arial, sans-serif", color="black"),
                title_x=0,  # Align title to the left
                title_xanchor='left',  # Anchor the title to the left side
                xaxis_title="Segment",
                yaxis_title="Event Count",
                xaxis=dict(
                    title_font=dict(size=14, family="Arial, sans-serif"),
                    tickfont=dict(size=12, family="Arial, sans-serif"),
                ),
                yaxis=dict(
                    title_font=dict(size=14, family="Arial, sans-serif"),
                    tickfont=dict(size=12, family="Arial, sans-serif"),
                ),
                legend=dict(
                    title="Segment",
                    font=dict(size=12, family="Arial, sans-serif"),
                ),
                margin=dict(t=40, b=40, l=40, r=40),  # Adjust margins
                plot_bgcolor="white",  # Set the background color to white
            )

            selected_segment_event = plotly_events(fig1, click_event=True, key="segment_event")

        # Initialize second chart data
        filtered_genre_data = state_segment_genre_counts

        # Update second chart based on clicks in the first chart
        if selected_segment_event:
            clicked_segment = selected_segment_event[0]["x"]  # Extract clicked segment

            # Filter genre data for the clicked segment
            if clicked_state:
                # Filter for the selected state and segment
                filtered_genre_data = state_segment_genre_counts[
                    (state_segment_genre_counts["venue_state"] == clicked_state) &
                    (state_segment_genre_counts["segment_name"] == clicked_segment)
                ]
                # Aggregate by genre to get the total event count per genre for the selected segment and state
                aggregated_genre_data = filtered_genre_data.groupby("genre_name", as_index=False)["total_events"].sum()
                title = f"Event Count by Genre in {clicked_segment} Segment ({clicked_state})"
            else:
                # Filter only by the clicked segment (all states)
                filtered_genre_data = state_segment_genre_counts[
                    state_segment_genre_counts["segment_name"] == clicked_segment
                ]
                # Aggregate by genre to get the total event count per genre for the selected segment (all states)
                aggregated_genre_data = filtered_genre_data.groupby("genre_name", as_index=False)["total_events"].sum()
                title = f"Event Count by Genre in {clicked_segment} Segment (All States)"

            # Update the second chart with aggregated genre data
            fig2 = px.bar(
                aggregated_genre_data,
                x="genre_name",
                y="total_events",
                color="genre_name",
                title=title,
                labels={"genre_name": "Genre", "total_events": "Event Count"},
                color_discrete_sequence=px.colors.qualitative.Light24,
            )


        # Expander for the second bar chart
        with st.expander('Select a Segment for More Detail', expanded=True):
            
            st.plotly_chart(fig2, use_container_width=True)
        
    
    



with attractions_tab:
    if selected_genre == "All":
        st.header(f"Top Attractions in {selected_segment}")
    else:
        st.header(f"Top Attractions in {selected_genre}")

    # numoto dispaly from 10 to 30 in steps of 5
    num_attractions = st.selectbox('Number of Genres to Display:', options=range(10, 31, 5))


    attractions_df = get_top_attractions(df, selected_segment, selected_genre, num_attractions)

    # format and displayt the top attractions
    st.table(attractions_df)