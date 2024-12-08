
import pandas as pd
import matplotlib.pyplot as plt

import matplotlib.pyplot as plt

def piechart_genres_and_attractions_by_segment_and_city(df, segment, city):
    """
    Analyze genres and attractions for a given segment and city, or all cities if city='all'.

    Args:
        df (pd.DataFrame): The input dataframe containing venue and genre data.
        segment (str): The genre segment to filter the data for.
        city (str): The city to filter the data for. If 'all', analyze all cities.

    Returns:
        tuple: A tuple containing the genre percentages (pd.Series) and the Matplotlib figure object.
    """
    # Filter data for the segment
    filtered_data = df[df['segment_name'] == segment]

    # Apply city filter if a specific city is provided
    if city.lower() != 'all':
        filtered_data = filtered_data[filtered_data['venue_city'] == city]

    if filtered_data.empty:
        print(f"No data available for {segment} and city '{city}'.")
        return None

    # Group by genre and calculate percentages
    genre_counts = filtered_data['genre_name'].value_counts()
    genre_percentages = (genre_counts / genre_counts.sum()) * 100

    # Group genres with less than 2.5% into "Other"
    genre_percentages = genre_percentages.apply(lambda x: x if x >= 2.5 else 0)
    genre_percentages['Other'] = 100 - genre_percentages.sum()
    genre_percentages = genre_percentages[genre_percentages > 0]

    # Create the pie chart without displaying it
    fig, ax = plt.subplots(figsize=(8, 8))
    genre_percentages.plot.pie(autopct='%1.1f%%', startangle=140, legend=False, ax=ax)
    ax.set_title(f"Most Popular Genres for Segment '{segment}' in {city.title() if city.lower() != 'all' else 'All Cities'}")
    ax.set_ylabel('')  # Hide the y-label for aesthetics

    # Return the genre percentages and the figure object
    return fig

