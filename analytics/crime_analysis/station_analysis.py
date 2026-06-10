import pandas as pd

def analyze_station_crimes(records: list[dict]) -> list[dict]:
    """
    Analyzes and groups crime count by police station.
    """
    if not records:
        return []
    df = pd.DataFrame(records)
    if 'station_name' not in df.columns or 'count' not in df.columns:
        return records
    df_grouped = df.groupby('station_name')['count'].sum().reset_index()
    df_grouped = df_grouped.sort_values(by='count', ascending=False)
    return df_grouped.to_dict(orient='records')
