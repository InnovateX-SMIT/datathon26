import pandas as pd

def aggregate_station_crime(records: list[dict]) -> list[dict]:
    """
    Station Aggregation.
    Groups by station and coordinates to compute aggregated crime counts.
    Supports raw or pre-aggregated query inputs.
    """
    if not records:
        return []
    df = pd.DataFrame(records)
    if 'station' not in df.columns:
        return []
        
    group_cols = ['station']
    if 'latitude' in df.columns and 'longitude' in df.columns:
        group_cols.extend(['latitude', 'longitude'])
        
    if 'crime_count' in df.columns:
        aggregated = df.groupby(group_cols)['crime_count'].sum().reset_index()
    else:
        aggregated = df.groupby(group_cols).size().reset_index(name='crime_count')
        
    aggregated = aggregated.sort_values(by='crime_count', ascending=False)
    return aggregated.to_dict(orient='records')

def get_station_statistics(records: list[dict]) -> dict:
    """
    Station Statistics.
    Computes overall summary statistics for station-level crime.
    """
    aggregated = aggregate_station_crime(records)
    if not aggregated:
        return {
            "total_stations": 0,
            "max_crime_station": None,
            "min_crime_station": None,
            "avg_crime_count": 0.0
        }
    df = pd.DataFrame(aggregated)
    return {
        "total_stations": int(len(df)),
        "max_crime_station": str(df.loc[df['crime_count'].idxmax(), 'station']) if not df.empty else None,
        "min_crime_station": str(df.loc[df['crime_count'].idxmin(), 'station']) if not df.empty else None,
        "avg_crime_count": float(df['crime_count'].mean()) if not df.empty else 0.0
    }
