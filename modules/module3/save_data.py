from modules.module3.savesubgraph import *



cities = ['Las Vegas', 'New York', 'Boston', 'Chicago', 'Philadelphia',
       'Los Angeles', 'Atlanta', 'Washington', 'Seattle', 'San Diego',
       'San Francisco', 'Houston', 'Dallas', 'Raleigh', 'Ft Lauderdale',
       'Indianapolis', 'Columbus', 'Detroit', 'Denver', 'Nashville']


# Create first graph visualizations
print('Saving subgraphs OPTION 1')
save_graph(cities_list=cities, option=1)

# Save OPTION 1 graph metrics
G = load_graph(city_filter='all', option=1)
save_degree_centrality(G, city_filter='all')

for city in cities:
    G = load_graph(city_filter=city, option = 1)
    save_degree_centrality(G, city_filter=city)


# Create second graph
print('Saving subgraphs OPTION 2')
save_graph(cities_list=cities, option = 2)

#Save OPTION 2 graph metrics
G = load_graph(city_filter='all', option=2)
save_clustering(G, city_filter='all')
save_edge_weight(G, city_filter='all')
save_comunities(G, city_filter='all')

for city in cities:
    G = load_graph(city_filter=city, option = 2)
    save_clustering(G, city_filter=city)
    save_edge_weight(G, city_filter=city)
    save_comunities(G, city_filter=city)



