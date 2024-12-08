from modules.module3.graph3 import *
import folium 
from folium import *  
from folium.plugins import Fullscreen
from branca.colormap import linear


# -------------------------------------------------------------------------------------------------------
#                                                STATE MAP
# -------------------------------------------------------------------------------------------------------

# Function to create the map 
def create_map_event_popularity_state(dataset, geojson_data):
    
    # Check that the information we have matches that of the geojson
    for feature in geojson_data["features"]:
        # Select the state in the GEOJSON
        state = feature["properties"]["ste_name"]
        # Check the state is also in our dataset
        states_data = dataset[dataset["venue_state"] == state]

        # Assign the number of events to each state 
        if not states_data.empty:
            feature["properties"]["total_events"] = int(states_data["total_events"].values[0])
        else:
            feature["properties"]["total_events"] = 0  # Use None to indicate missing data

    # Create a folium map centered on the United States
    m = folium.Map(location=[37.8, -96], zoom_start=4, tiles="cartodbpositron")

    # Add choropleth layer with a color palette
    choropleth = Choropleth(
        geo_data=geojson_data,
        name="choropleth",
        data=dataset,
        columns=["venue_state", "total_events"],
        key_on="feature.properties.ste_name",
        fill_color="YlGnBu",  
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Total Number of Events per State"
    ).add_to(m)

    # Add tooltips and gray styling for states with no data
    folium.GeoJson(
        geojson_data,
        style_function=lambda x: {
            "fillColor": "#D3D3D3" if x["properties"]["total_events"] is 0 else choropleth.color_scale(
                x["properties"]["total_events"]
            ),
            "color": "black",
            "weight": 0.5,
            "fillOpacity": 0.7 if x["properties"]["total_events"] is not 0 else 0.5
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["ste_name", "total_events"],
            aliases=["State: ", "Number of Events: "],
            localize=True
        )
    ).add_to(m)

    # Add fullscreen button
    Fullscreen().add_to(m)

    return m
