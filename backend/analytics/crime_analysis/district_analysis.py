import pandas as pd

def analyze_district_crimes(records: list[dict]) -> list[dict]:
    """
    Analyzes and groups crime count by district.
    """
    if not records:
        return []
    df = pd.DataFrame(records)
    if 'district' not in df.columns or 'count' not in df.columns:
        return records
    df_grouped = df.groupby('district')['count'].sum().reset_index()
    df_grouped = df_grouped.sort_values(by='count', ascending=False)
    return df_grouped.to_dict(orient='records')
