from module3.graph3 import *
import pickle
import os

def save_graph(cities_list, option = 1):
    # Load the data
    data = load_data()  # Load data using the function from the module
    # Create the graph
    data_dict = create_dict(data, city_filter=cities_list)
    if option == 1:
        G = create_graph3(data, data_dict, option=option)
        pickle.dump(G, open('data/graphs/all.pickle', 'wb'))
        for city in cities_list:
            G1 = create_subgraph(G, city)
            if G1:
                pickle.dump(G1, open(f'data/graphs/{city}.pickle', 'wb'))
    elif option == 2:
        G = create_graph3(data, data_dict, option=option)
        pickle.dump(G, open('data/graphs2/all.pickle', 'wb'))
        for city in cities_list:
            G1 = create_subgraph(G, city)
            if G1:
                pickle.dump(G1, open(f'data/graphs2/{city}.pickle', 'wb'))



def load_graph(city_filter, option = 1):
    # load graph object from file
    if os.path.isfile(f'data/graphs/{city_filter}.pickle') or os.path.isfile(f'data/graphs2/{city_filter}.pickle'):
        if option == 1:
            G = pickle.load(open(f'data/graphs/{city_filter}.pickle', 'rb'))
        elif option == 2:
            G = pickle.load(open(f'data/graphs2/{city_filter}.pickle', 'rb'))
        return G
    else:
        print('No file with city ', city_filter)

def save_degree_centrality(G, city_filter):
    sorted_centrality, nodes_names = calculate_degree_centrality(G)
    nodes_id = [t[0] for t in sorted_centrality]
    nodes_centrality = [t[1] for t in sorted_centrality]
    df = pd.DataFrame({'node_id': nodes_id, 'node_centrality': nodes_centrality, 'node_name': nodes_names})
    df.to_csv(f'data/degree_centrality/{city_filter}.csv')


def save_clustering(G, city_filter):
    cluster_coeff, id_to_name = weighted_clustering_coefficient(G)
    nodes_id = [t[0] for t in cluster_coeff]
    nodes_coeff = [t[1] for t in cluster_coeff]
    nodes_names = [id_to_name[t[0]] for t in cluster_coeff]
    df = pd.DataFrame({'node_id': nodes_id, 'node_coeff': nodes_coeff, 'node_name': nodes_names})
    df.to_csv(f'data/cluster_coeff/{city_filter}.csv')


def save_edge_weight(G, city_filter):
    edge_weights_analysis, edge_weights = edge_weight_analysis(G)
    pickle.dump(edge_weights_analysis, open(f'data/edge_weights/analysis/{city_filter}.pickle', 'wb'))
    pickle.dump(edge_weights, open(f'data/edge_weights/{city_filter}.pickle', 'wb'))


def save_comunities(G, city_filter):
    comunities = community_detection(G)
    pickle.dump(comunities, open(f'data/comunities/{city_filter}.pickle', 'wb'))



