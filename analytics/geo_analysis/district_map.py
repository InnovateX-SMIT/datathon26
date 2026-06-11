import pandas as pd

def aggregate_district_crime(records: list[dict]) -> list[dict]:
    """
    District Aggregation & Crime Count Calculation.
    Handles raw records (by counting rows per district) or pre-aggregated records
    (by grouping and summing existing crime counts).
    """
    if not records:
        return []
    df = pd.DataFrame(records)
    if 'district' not in df.columns:
        return []
        
    if 'crime_count' in df.columns:
        # Pre-aggregated from SQL
        aggregated = df.groupby('district')['crime_count'].sum().reset_index()
    else:
        # Raw records
        aggregated = df.groupby('district').size().reset_index(name='crime_count')
        
    aggregated = aggregated.sort_values(by='crime_count', ascending=False)
    return aggregated.to_dict(orient='records')

def get_district_metrics(records: list[dict]) -> dict:
    """
    District Metrics.
    Computes overall summary statistics for district-level crime.
    """
    aggregated = aggregate_district_crime(records)
    if not aggregated:
        return {
            "total_districts": 0,
            "max_crime_district": None,
            "min_crime_district": None,
            "avg_crime_count": 0.0
        }
    df = pd.DataFrame(aggregated)
    return {
        "total_districts": int(len(df)),
        "max_crime_district": str(df.loc[df['crime_count'].idxmax(), 'district']) if not df.empty else None,
        "min_crime_district": str(df.loc[df['crime_count'].idxmin(), 'district']) if not df.empty else None,
        "avg_crime_count": float(df['crime_count'].mean()) if not df.empty else 0.0
    }
