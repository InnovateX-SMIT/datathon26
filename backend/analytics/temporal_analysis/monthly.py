import pandas as pd

def aggregate_monthly_trends(data):
    """
    Placeholder matching initial function definition if imported elsewhere.
    """
    return analyze_monthly_trends(data)

def analyze_monthly_trends(records: list[dict]) -> list[dict]:
    """
    Aggregates or formats monthly trends.
    records is a list of dicts with 'period' and 'count'.
    """
    if not records:
        return []
    df = pd.DataFrame(records)
    if 'period' not in df.columns or 'count' not in df.columns:
        return records
    df = df.sort_values(by='period')
    return df.to_dict(orient='records')
