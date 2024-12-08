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
import pickle


def load_data():
    # load data
    data = pd.read_csv('data/events_usa_clean.csv')
    return data

def load_genre_attraction_graph(city, segment):
    return pickle.load(open(f'data/graphs1/{city}_{segment}.pickle', 'rb'))

def load_genre_centrality(city, segment):
    with open(f'data/genre_popularity/{city}_{segment}.txt', 'r') as f:
        genre_popularity = f.readlines()
    return genre_popularity
