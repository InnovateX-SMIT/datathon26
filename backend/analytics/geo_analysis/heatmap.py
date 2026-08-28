import pandas as pd

def generate_heatmap_json(records: list[dict]) -> list[dict]:
    """
    Heatmap Point Generation & Crime Density Calculation.
    Aggregates latitude and longitude coordinates and returns weighted points representing crime density.
    """
    if not records:
        return []
    df = pd.DataFrame(records)
    if 'latitude' not in df.columns or 'longitude' not in df.columns:
        return []
        
    if 'weight' in df.columns:
        grouped = df.groupby(['latitude', 'longitude'])['weight'].sum().reset_index()
    elif 'crime_count' in df.columns:
        grouped = df.groupby(['latitude', 'longitude'])['crime_count'].sum().reset_index(name='weight')
    else:
        grouped = df.groupby(['latitude', 'longitude']).size().reset_index(name='weight')
        
    return grouped.to_dict(orient='records')
