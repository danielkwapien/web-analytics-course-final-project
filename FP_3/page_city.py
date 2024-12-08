import streamlit as st
from module3.savesubgraph import *
from module3.graph3 import * 
from utils import *
from attractions_module.graph1 import *
from popularity_module.genre_popularity import *

st.title("City Events Analysis")


cities = ['all', 'Las Vegas', 'New York', 'Boston', 'Chicago', 'Philadelphia',
       'Los Angeles', 'Atlanta', 'Washington', 'Seattle', 'San Diego',
       'San Francisco', 'Houston', 'Dallas', 'Raleigh', 'Ft Lauderdale',
       'Indianapolis', 'Columbus', 'Detroit', 'Denver', 'Nashville']


selected_city = st.selectbox("Select a City to Filter", cities)
df= load_data()
segments = df.groupby(['segment_name'])['genre_name'].apply(set).to_dict()
# Allow the user to select a segment dynamically
selected_segment = st.selectbox("Select a Segment", list(segments.keys()))


if selected_city != 'all':

    st.header(f"Genre Price Range in {selected_city}")
    with st.expander("Genre price range plots", expanded=True):

        # Streamlit layout for tab selection
        tab1, tab2 = st.tabs(['Price Range per Genre', 'Min and Max Price per Genre'])

        # Tab 1: Price Range per Genre
        with tab1:
            fig = price_range_graph(df, segments, selected_segment, selected_city)
            # Display the Plotly figure in Streamlit
            st.plotly_chart(fig)

        with tab2:
            # Plot Min and Max Prices using Plotly
            fig = min_max_price_graph(df, segments, selected_segment, selected_city)
            st.plotly_chart(fig)


    st.header(f"Venue Relationships for {selected_segment} Genres in {selected_city}")
    # Plot venue genre graph

    st.subheader(f"Venue Genre Graph in {selected_city}")
    with st.expander("Venue - Gemre graph", expanded=True):
        G1 = load_graph(selected_city, option=1)
        fig = interactive_venue_graph_with_colored_edges(G1)

        # Display the graph
        st.plotly_chart(fig)


degree_centrality = pd.read_csv(f'data/degree_centrality/{selected_city}.csv', index_col=0)

# Interactive Table
st.subheader(f"Centrality Table for {selected_city}")
# selected_number = st.selectbox('Nodes in Top:', options = range(1,21))
# default should be 10

with st.expander("Centrality table", expanded=True):
    selected_number = st.selectbox('Nodes in Top:', options = range(1,21), index=9)
    st.dataframe(degree_centrality[['node_name', 'node_centrality']].sort_values(by='node_centrality', ascending=False)['node_name'].head(selected_number))


# Display the clustering coefficient as a bar chart
clustering_df = pd.read_csv(f'data/cluster_coeff/{selected_city}.csv', index_col=0)
clustering_df_filtered = clustering_df.loc[clustering_df['node_coeff'] > 0]

# Display Top Nodes
st.subheader(f"Clustering Coefficient for {selected_city}")

with st.expander("Clustering coefficients information", expanded=True):

    tab1, tab2 = st.tabs(['Top Nodes', 'Distribution'])

    with tab1:
        st.markdown(f"#### Clustering Coefficient Top Nodes for {selected_city}")
        # Get the top 10 nodes by clustering coefficient
        top_nodes = clustering_df_filtered.nlargest(10, 'node_coeff')

        # Create two columns for displaying names and coefficients
        col1, col2 = st.columns(2)

        # Display data in two columns with some styling
        with col1:
            for idx, row in top_nodes.iterrows():
                st.write(f"**{row['node_name']}**")

        with col2:
            for idx, row in top_nodes.iterrows():
                st.write(f"{row['node_coeff']:.4f}")

    with tab2:
        st.markdown(f"#### Clustering Coefficient Distribution for {selected_city}")
        hist_fig = px.histogram(
            clustering_df_filtered,
            x='node_coeff',
            nbins=10,
            title="Distribution of Clustering Coefficients",
            labels={"node_coeff": "Clustering Coefficient"}
        )
        st.plotly_chart(hist_fig, use_container_width=True)


# Plot the distribution of clustering coefficients
# st.subheader(f"Clustering Coefficient Distribution for {selected_city}")
# hist_fig = px.histogram(
#     clustering_df_filtered,
#     x='node_coeff',
#     nbins=10,
#     title="Distribution of Clustering Coefficients",
#     labels={"node_coeff": "Clustering Coefficient"}
# )
# st.plotly_chart(hist_fig, use_container_width=True)


if selected_city != 'all':
    st.subheader(f"Comunity detection in Venues for {selected_city}")
    with st.expander("community detection in venues", expanded=True):

        G2 = load_graph(selected_city, option=2)

        # TODO fix, the nodes display the id not the name
        communities = pickle.load(open(f'data/comunities/{selected_city}.pickle', 'rb'))

        fig2 = interactive_community_graph(G2, communities)
        st.plotly_chart(fig2)



st.header(f"Genre Attraction Analysis in {selected_city}")

G = load_genre_attraction_graph(selected_city, selected_segment)

if selected_city!='all':
    st.subheader(f"Genre Attraction Graph in {selected_city} for {selected_segment}")
    
    with st.expander("Genre Attraction Graph", expanded=True):
        fig = interactive_attraction_plot(G)
        st.plotly_chart(fig)


genre_popularity = calculate_genre_centrality(G)

st.subheader(f"Genre Popularity in {selected_city} for {selected_segment}")

with st.expander("Genres Popularity Table", expanded=True):

    tab_popularity, tab_niche = st.tabs(['Most popular', 'Niche genres'])
            
    num_display = st.selectbox('Number of Genres to Display:', options = range(1,21), index=6)


    with tab_popularity:
        st.markdown(f"#### Most Popular Genres in {selected_city}")
        for name, _ in genre_popularity[:num_display]:
            st.write(f"- {name}")

    with tab_niche:
        st.markdown(f"#### Niche Genres in {selected_city}")
        # st.dataframe(pd.DataFrame(genre_popularity).tail(num_display))
        for name, _ in genre_popularity[-num_display:]:
            st.write(f"- {name}")

with st.expander("Genres Piechart", expanded=True):
    piechart = piechart_genres_and_attractions_by_segment_and_city(df, selected_segment, selected_city)
    if piechart:
        st.pyplot(piechart)
    
