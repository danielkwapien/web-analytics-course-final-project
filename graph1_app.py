
# module for main streamlit app pipeline for graph 1 Artists - Genre


import streamlit as st
from graph1 import load_data, create_graph, interactive_plot, calculate_genre_centrality, find_bridge_artists

# Title of the app
st.title("Interactive Performer-Genre Graph")

# Load the data
data = load_data()  # Load data using the function from the module

# Create the graph
G = create_graph(data)

# Display the interactive graph
st.subheader("Interactive Graph")
fig = interactive_plot(G)
st.plotly_chart(fig)

# Calculate genre centrality
all_genres = calculate_genre_centrality(G)

# Separate popular and niche genres
popular_genres = all_genres[:5]
niche_genres = all_genres[-5:]

# Display genres in two columns
st.subheader("Genre Centrality Analysis")
col1, col2 = st.columns(2)

with col1:
    st.write("### Niche Genres")
    for genre, _ in niche_genres:
        st.markdown(f"- **{genre}**")

with col2:
    st.write("### Popular Genres")
    for genre, _ in popular_genres:
        st.markdown(f"- **{genre}**")

# Display bridge artists
st.subheader("Artists Acting as Bridges Between Genres")
bridge_artists = find_bridge_artists(G)
if bridge_artists:
    for artist, genres in bridge_artists:
        st.markdown(f"**{artist}** bridges genres: {', '.join(genres)}")
else:
    st.write("No artists found acting as bridges between genres.")

# Dropdown to select a genre and view associated artists
st.subheader("Find Artists by Genre")

# dropdown to select a genre alphabetically
ordered_genres = sorted(data['Genre'].unique())


selected_genre = st.selectbox("Select a Genre", ordered_genres)

# Find artists connected to the selected genre
artists_in_genre = [
    neighbor for neighbor in G.neighbors(selected_genre)
    if G.nodes[neighbor].get("type") == "artist"
]

st.write(f"### Artists in {selected_genre}")
if artists_in_genre:
    for artist in artists_in_genre:
        st.markdown(f"- **{artist}**")
else:
    st.write("No artists found for this genre.")

