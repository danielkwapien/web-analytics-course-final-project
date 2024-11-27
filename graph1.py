import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import networkx as nx
import json

def load_data():
    # load data
    data = pd.read_csv(r'final project\data\artist_genre_data.csv')
    return data


def create_graph(artist_genre_data):
    # Create a new graph
    G = nx.Graph()

    # Add nodes and edges to the graph
    for _, row in artist_genre_data.iterrows():
        artist = row['artist_name']
        genre = row['Genre']

        # Add nodes for artist and genre
        G.add_node(artist, type='artist')
        G.add_node(genre, type='genre')

        # Add an edge between the artist and the genre
        G.add_edge(artist, genre)

    return G

def simple_plot(G):
    # Plot the graph
    plt.figure(figsize=(12, 12))  # Set the figure size

    # Position nodes using a layout algorithm
    pos = nx.spring_layout(G)  # Spring layout for a nice visualization

    # Draw the nodes and edges
    nx.draw_networkx_nodes(G, pos, node_size=50, node_color="skyblue", alpha=0.8)
    nx.draw_networkx_edges(G, pos, alpha=0.5)

    # Add labels to the graph
    # Only label genres to reduce clutter
    labels = {node: node for node, attr in G.nodes(data=True) if attr["type"] == "genre"}
    nx.draw_networkx_labels(G, pos, labels, font_size=10, font_color="darkblue")

    # Display the plot
    plt.title("Performer-Genre Relationship Graph", fontsize=16)
    plt.axis("off")  # Turn off the axis
    plt.show()

def interactive_plot(G):
    # Get positions for nodes
    pos = nx.spring_layout(G)

    # Prepare node traces for Plotly
    node_x = []
    node_y = []
    node_labels = []
    node_hover = []
    node_colors = []

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

        # Check node type and assign hover text and color accordingly
        if G.nodes[node].get('type') == 'artist':
            node_hover.append(f"Artist: {node}")
            node_colors.append('skyblue')
        elif G.nodes[node].get('type') == 'genre':
            node_hover.append(f"Genre: {node}")
            node_colors.append('orange')
        else:
            node_hover.append(f"Node: {node}")
            node_colors.append('gray')  # Default color if type is undefined

        # Use the node name as the label
        node_labels.append(node)

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers',
        marker=dict(
            size=10,
            color=node_colors,
            line_width=1
        ),
        text=node_labels,
        hovertext=node_hover,
        hoverinfo="text"
    )

    # Prepare edge traces for Plotly
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
        hoverinfo="none",
        mode="lines"
    )

    # Create the Plotly figure
    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title="Performer-Genre Interactive Graph",
                        titlefont_size=16,
                        showlegend=False,
                        hovermode="closest",
                        margin=dict(b=0, l=0, r=0, t=40),
                        xaxis=dict(showgrid=False, zeroline=False),
                        yaxis=dict(showgrid=False, zeroline=False)
                    ))

        # Return the Plotly figure 
        #fig.show()
    
    return fig


def calculate_genre_centrality(G):
    """
    Calculates degree centrality for genre nodes and returns
    all genres sorted by centrality in descending order, excluding 'Other'.
    """
    # Compute degree centrality
    centrality = nx.degree_centrality(G)

    # Filter for genre nodes and exclude 'Other'
    genre_centrality = {
        node: centrality[node]
        for node, attr in G.nodes(data=True)
        if attr.get("type") == "genre" and node != "Other" # exclude other from the genres
    }

    # Sort genres by centrality in descending order
    sorted_genres = sorted(genre_centrality.items(), key=lambda x: x[1], reverse=True)

    # Return sorted list of genres
    return sorted_genres



def find_bridge_artists(G):
    """
    Identifies artist nodes that act as bridges between two genres.
    Returns a list of tuples (artist, [genre1, genre2]).
    """
    bridge_artists = []

    # Iterate over artist nodes
    for node, attr in G.nodes(data=True):
        if attr.get("type") == "artist":
            # Find connected genres
            connected_genres = [
                neighbor for neighbor in G.neighbors(node)
                if G.nodes[neighbor].get("type") == "genre"
            ]

            # If the artist connects exactly two genres, it's a bridge
            if len(connected_genres) == 2:
                bridge_artists.append((node, connected_genres))

    return bridge_artists
