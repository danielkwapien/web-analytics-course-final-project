


# per city per segment of the data, save the graphs and their info for faster retrival

cities = ['Las Vegas', 'New York', 'Boston', 'Chicago', 'Philadelphia',
       'Los Angeles', 'Atlanta', 'Washington', 'Seattle', 'San Diego',
       'San Francisco', 'Houston', 'Dallas', 'Raleigh', 'Ft Lauderdale',
       'Indianapolis', 'Columbus', 'Detroit', 'Denver', 'Nashville']


from attractions_module.graph1 import *
from utils import *
import pickle

data = load_data()

segments = data['segment_name'].unique()

def save_attracion_genre_graph(city, segment, data):
    data = data[data['city'] == city]
    data = data[data['segment_name'] == segment]
    G = create_attraction_genre_graph(segment, data)
    pickle.dump(G, open(f'data/graphs1/{city}_{segment}.pickle', 'wb'))
    print(f'Saved graph for {city} and {segment}')

# load fnciton is in utils


for city in cities:
    for segment in segments:
        save_attracion_genre_graph(city, segment, data)
        G = load_genre_attraction_graph(city, segment)


print('Done')

