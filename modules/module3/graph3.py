import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import networkx as nx
import json
import matplotlib.colors as mcolors
from community import community_louvain  
import plotly.express as px


def load_data():
    # load data
    data = pd.read_csv('data/events_usa_clean.csv')
    return data


def create_dict(venue_event_df, city_filter=None):
    if city_filter:
        venues_dict = venue_event_df.loc[venue_event_df['venue_city'].isin(city_filter)].groupby('venue_id')['genre_name'].apply(set).to_dict()
    else:
        venues_dict = venue_event_df.groupby('venue_id')['genre_name'].apply(set).to_dict()

    return venues_dict


def create_graph3(venue_event_df, venues_dict, option = 1):
    G = nx.Graph()
    for index, row in venue_event_df.iterrows():
        venue_id = row['venue_id']
        venue_name = row['venue_name']
        venue_state = row['venue_state']
        venue_city = row['venue_city']
        G.add_node(venue_id, name=venue_name, state=venue_state, city=venue_city)

    #OPITON 1: one edge for each genre
    if option == 1:
        for v1 in venues_dict:
            for v2 in venues_dict:
                if v1 != v2:
                    common_genres = set(venues_dict[v1]) & set(venues_dict[v2])
                    for genre in common_genres:
                        G.add_edge(v1, v2, label=genre)

    #OPTION 2: edge if some genre in common, edge weight indicating the number of genres in common
    elif option == 2:
        for v1 in venues_dict:
            for v2 in venues_dict:
                if v1 != v2:
                    common_genres = set(venues_dict[v1]) & set(venues_dict[v2])
                    if common_genres:
                        G.add_edge(v1, v2, weight=len(common_genres))

    else:
        raise(ValueError, 'The option value provided is not available: ', option)

    return G



def create_subgraph(G, city_filter):
    filtered_nodes = [node for node, data in G.nodes(data=True) if data.get("city") == city_filter]
    if filtered_nodes:
        G1 = G.subgraph(filtered_nodes)
        return G1
    else:
        print('No cities with name ', city_filter)
        return None


def price_range_graph(df, segments, selected_segment, selected_city):
    
    # Filter data for the selected segment and corresponding genres
    selected_genres = segments[selected_segment]
    filtered_df = df[df['segment_name'] == selected_segment]
    filtered_df = filtered_df[filtered_df['venue_city'] == selected_city]

    # Group by genre and get the min and max price for each genre
    price_range_per_genre = filtered_df.groupby('genre_name')[['min_price', 'max_price']].agg(['min', 'max'])

    # Calculate the price range (difference between max and min price)
    price_range_per_genre['price_range'] = price_range_per_genre['max_price']['max'] - price_range_per_genre['min_price']['min']

    # Sort by price range
    price_range_df = price_range_per_genre[['price_range']].sort_values(by='price_range', ascending=False).reset_index()

    # Plot using Plotly
    fig = px.bar(price_range_df, 
                x='price_range', 
                y='genre_name', 
                orientation='h', 
                title=f'Price Range per Genre in {selected_segment}',
                labels={'price_range': 'Price Range', 'genre_name': 'Genre'},
                color='price_range',
                color_continuous_scale='Viridis')
    return fig

def min_max_price_graph(df, segments, selected_segment, selected_city):
    
    # Filter data for the selected segment and corresponding genres
    selected_genres = segments[selected_segment]
    filtered_df = df[df['segment_name'] == selected_segment]
    filtered_df = filtered_df[filtered_df['venue_city'] == selected_city]

    # Group by genre and get the min and max price for each genre
    price_range_per_genre = filtered_df.groupby('genre_name')[['min_price', 'max_price']].mean()
    fig = px.bar(price_range_per_genre, 
                  x=price_range_per_genre.index, 
                  y=['min_price', 'max_price'],
                  barmode='group',
                  title=f'Min and Max Price per Genre in {selected_segment}',
                  labels={'value': 'Price', 'genre_name': 'Genre'},
                  color_discrete_map={'min_price': 'lightblue', 'max_price': 'darkblue'})
    
    return fig    



def interactive_venue_graph_with_colored_edges(G):
    """
    Create an interactive Plotly graph visualization for the venue-event dataset with colored edges by genre.

    Args:
        G (networkx.Graph): The graph object representing venues and their relationships.

    Returns:
        plotly.graph_objects.Figure: An interactive Plotly figure.
    """

    # Define a color palette for genres
    color_palette = list(mcolors.TABLEAU_COLORS.values())  # Get a list of Tableau colors
    genre_to_color = {}

    # Assign a unique color to each genre
    unique_genres = set(nx.get_edge_attributes(G, "label").values())
    for i, genre in enumerate(unique_genres):
        genre_to_color[genre] = color_palette[i % len(color_palette)]  # Cycle through the palette if needed

    # Get positions for nodes
    pos = nx.spring_layout(G, seed = 42)

    # Prepare node traces for Plotly
    node_x = []
    node_y = []
    node_hover = []
    node_colors = []

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

        # Hover text includes venue name and city
        name = G.nodes[node].get("name", "Unknown Venue")
        city = G.nodes[node].get("city", "Unknown City")
        node_hover.append(f"Venue: {name}<br>City: {city}")

        # Node color (can be customized further)
        node_colors.append("skyblue")

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers',
        marker=dict(
            size=15,
            color=node_colors,
            line_width=1
        ),
        hovertext=node_hover,
        hoverinfo="text"
    )

    # Prepare edge traces for Plotly (one trace per genre)
    edge_traces = []
    for genre, color in genre_to_color.items():
        edge_x = []
        edge_y = []

        for edge in G.edges(data=True):
            if edge[2].get("label") == genre:
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.append(x0)
                edge_x.append(x1)
                edge_x.append(None)
                edge_y.append(y0)
                edge_y.append(y1)
                edge_y.append(None)

        edge_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            line=dict(width=1, color=color),
            hoverinfo="text",
            mode="lines",
            name=genre  # Legend entry for each genre
        )
        edge_traces.append(edge_trace)

    # Create the Plotly figure
    fig = go.Figure(
        data=[*edge_traces, node_trace],
        layout=go.Layout(
            title="Venue-Genre Interactive Graph with Colored Edges",
            titlefont_size=16,
            showlegend=True,
            hovermode="closest",
            margin=dict(b=0, l=0, r=0, t=40),
            xaxis=dict(showgrid=False, zeroline=False),
            yaxis=dict(showgrid=False, zeroline=False)
        )
    )

    return fig



def interactive_community_graph(G, communities):
    """
    Create an interactive Plotly graph with nodes colored by community.

    Args:
        G (networkx.Graph): The input graph.
        communities (dict): A mapping of nodes to community IDs.

    Returns:
        plotly.graph_objects.Figure: An interactive graph.
    """
    # Generate positions for the graph layout
    pos = nx.spring_layout(G, seed=42)  # Fixed seed for consistent layout
    attributes = nx.get_node_attributes(G, 'name')

    # Prepare node trace data
    node_x = []
    node_y = []
    node_colors = []
    node_texts = []

    # Map each community to a distinct color
    community_colors = {}
    unique_communities = set(communities.values())
    color_palette = px.colors.qualitative.Plotly  # Use Plotly's default qualitative palette
    for i, community in enumerate(unique_communities):
        community_colors[community] = color_palette[i % len(color_palette)]

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        community = communities[node]
        node_colors.append(community_colors[community])
        node_texts.append(f"Node: {attributes[node]}<br>Community: {community}")

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers',
        marker=dict(
            size=15,
            color=node_colors,  # Use community color
            line_width=2
        ),
        text=node_texts,
        hoverinfo='text'
    )

    # Prepare edge trace data
    edge_x = []
    edge_y = []

    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=0.5, color="#888"),
        hoverinfo='none',
        mode='lines'
    )

    # Create the Plotly figure
    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title="Interactive Community Graph",
                        titlefont_size=16,
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=0, l=0, r=0, t=40),
                        xaxis=dict(showgrid=False, zeroline=False),
                        yaxis=dict(showgrid=False, zeroline=False)
                    ))

    return fig


# Plot Graph with Degree Centrality
def plot_degree_centrality(G, centrality, highlight_nodes):
    pos = nx.spring_layout(G, seed=42)  # Layout for the graph
    
    # Create a Plotly scatter plot for nodes
    node_x = []
    node_y = []
    node_size = []
    node_color = []
    node_label = []
    
    for node, (x, y) in pos.items():
        node_x.append(x)
        node_y.append(y)
        node_size.append(centrality[node] * 500)  # Scale centrality for visualization
        node_color.append('red' if node in highlight_nodes else 'blue')
        node_label.append(G.nodes[node].get('label', str(node)))

    # Edges
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    # Node Trace
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        marker=dict(
            size=node_size,
            color=node_color,
            line_width=2,
        ),
        text=node_label,
        hoverinfo='text'
    )

    # Create the figure
    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=0, l=0, r=0, t=0),
                        xaxis=dict(showgrid=False, zeroline=False),
                        yaxis=dict(showgrid=False, zeroline=False),
                    ))

    return fig




#------------------------------------------
# ANALYSIS FUNCTIONS
#------------------------------------------

def community_detection(G):
    """
    Detect communities in a graph using the Louvain algorithm.

    Args:
        G (networkx.Graph): The input graph.

    Returns:
        dict: A mapping of nodes to their community IDs.
    """
    return community_louvain.best_partition(G, weight='weight')


def calculate_degree_centrality(G):
    """
    Calculate the degree centrality of nodes in a graph and return them in descending order.

    Args:
        G (networkx.Graph): The input graph.

    Returns:
        list: A list of tuples, where each tuple contains a node and its degree centrality,
              sorted in descending order of centrality.
        list: A list of the sorted centrality node names.
    """

    # Calculate degree centrality
    centrality = nx.degree_centrality(G)
    
    # Sort the nodes by centrality in descending order
    sorted_centrality = sorted(centrality.items(), key=lambda item: item[1], reverse=True)
    sorted_centrality_names = []
    attributes = nx.get_node_attributes(G, 'name')
    for nodeid in sorted_centrality:
        sorted_centrality_names.append(attributes[nodeid[0]])


    return sorted_centrality, sorted_centrality_names



def edge_weight_analysis(G):
    """
    Analyze edge weights in the graph to identify strongest and weakest connections.

    Args:
        G (networkx.Graph): The input weighted graph.

    Returns:
        dict: Dictionary containing strongest and weakest edges.
        list: A list containing the sorted weight analysis tuples, with both node names and the weight value.
    """
    # Extract all edges and their weights
    edge_weights = [(u, v, d['weight']) for u, v, d in G.edges(data=True)]
    
    # Sort edges by weight
    edge_weights_sorted = sorted(edge_weights, key=lambda x: x[2], reverse=True)
    
    # Strongest and weakest edges
    strongest_edges = edge_weights_sorted[:5]  # Top 5 strongest
    weakest_edges = edge_weights_sorted[-5:]  # Bottom 5 weakest
    
    attributes = nx.get_node_attributes(G, 'name')
    strongest_edges_names = []
    weakest_edges_names = []
    edge_weight_names = []

    for i in range(len(edge_weights_sorted)):
        edge = edge_weights_sorted[i]
        t = []
        t += [attributes[edge[0]]]
        t += [attributes[edge[1]]]
        t += [edge[2]]
        edge_weight_names.append(t)


    for edge in strongest_edges:
        strongest_edges_names.append((attributes[edge[0]], attributes[edge[1]], edge[2]))
    for edge in weakest_edges:
        weakest_edges_names.append((attributes[edge[0]], attributes[edge[1]], edge[2]))

    return {
        "strongest_edges": strongest_edges_names,
        "weakest_edges": weakest_edges_names
    }, edge_weight_names


def community_detection(G):
    """
    Detect communities using the Louvain algorithm.

    Args:
        G (networkx.Graph): The input graph.

    Returns:
        dict: Mapping of node to its community.
    """
    try:
        import community as community_louvain  # Install python-louvain: pip install python-louvain
    except ImportError:
        raise ImportError("Please install the python-louvain package to use this feature: pip install python-louvain")
    
    # Compute the best partition of the graph
    partition = community_louvain.best_partition(G, weight='weight')
    
    return partition


def weighted_clustering_coefficient(G):
    """
    Calculate the weighted clustering coefficient for all nodes.

    Args:
        G (networkx.Graph): The input weighted graph.

    Returns:
        dict: Mapping of node to its weighted clustering coefficient.
        dict: Mapping of node id to its name.
    """

    cluster_coeff = nx.clustering(G, weight='weight')
    cluster_coeff = sorted(cluster_coeff.items(), key=lambda x: x[1], reverse=True)

    id_to_name = nx.get_node_attributes(G, 'name')
    
    return cluster_coeff, id_to_name
