

def get_top_attractions(df, segment, genre, num_results=10):
    if genre != 'All':
        filtered_df = df[(df['segment_name'] == segment) & (df['genre_name'] == genre)]
    else:
        filtered_df = df[df['segment_name'] == segment]
    
    # Group by attraction_name to compute relevant stats
    top_attractions = (
        filtered_df.groupby('attraction_name')
        .agg(
            venue_state=('venue_state', lambda x: ', '.join(sorted(set(x)))),
            avg_min_price=('min_price', 'mean'),
            avg_max_price=('max_price', 'mean'),
            count=('attraction_name', 'size')  # Used for sorting
        )
        .sort_values(by='count', ascending=False)  # Sort by count
        .head(num_results)  # Limit to top attractions
        .reset_index()  # Reset index to make attraction_name a column
        .drop(columns='count')  # Drop the count column after sorting
    )
    
    top_attractions.rename(
        columns={
            'attraction_name': 'Attraction/Artist',
            'venue_state': 'State/s',
            'avg_min_price': 'Min price Avg',
            'avg_max_price': 'Max price Avg',
        },
        inplace=True
    )
    
    # Format prices to 2 decimals
    top_attractions['Min price Avg'] = top_attractions['Min price Avg'].apply(lambda x: round(x, 2))
    top_attractions['Max price Avg'] = top_attractions['Max price Avg'].apply(lambda x: round(x, 2))
    
    return top_attractions
    
    return top_attractions