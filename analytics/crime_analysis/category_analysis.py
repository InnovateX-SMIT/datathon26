import pandas as pd

def process_category_distribution(records: list[dict], limit: int = 10) -> list[dict]:
    """
    Given a list of category counts, sorts descending, takes top N, and formats.
    """
    if not records:
        return []
    df = pd.DataFrame(records)
    if 'name' not in df.columns or 'count' not in df.columns:
        return records
    df = df.sort_values(by='count', ascending=False)
    return df.head(limit).to_dict(orient='records')

def process_subcategory_distribution(records: list[dict], limit: int = 10) -> list[dict]:
    """
    Given a list of subcategory counts, sorts descending, takes top N, and formats.
    """
    if not records:
        return []
    df = pd.DataFrame(records)
    if 'name' not in df.columns or 'count' not in df.columns:
        return records
    df = df.sort_values(by='count', ascending=False)
    return df.head(limit).to_dict(orient='records')
