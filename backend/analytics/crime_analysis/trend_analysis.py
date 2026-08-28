import pandas as pd
import numpy as np

def calculate_trend_summary(daily_records: list[dict]) -> str:
    """
    Calculates a brief trend summary based on recent daily data.
    """
    if not daily_records or len(daily_records) < 2:
        return "No sufficient trend data available"
    
    df = pd.DataFrame(daily_records)
    # Ensure columns exist
    if 'period' not in df.columns or 'count' not in df.columns:
        return "Data format incorrect for trend analysis"
        
    df = df.sort_values(by='period')
    
    counts = df['count'].values
    if len(counts) >= 7:
        recent = counts[-7:]
        prev = counts[-14:-7] if len(counts) >= 14 else counts[:-7]
        recent_sum = sum(recent)
        prev_sum = sum(prev) if len(prev) > 0 else 0
        
        change = calculate_percentage_change(recent_sum, prev_sum)
        direction = "increase" if change > 0 else "decrease" if change < 0 else "stable"
        return f"{direction.capitalize()} of {abs(change):.1f}% in the last 7 days compared to prior period"
    else:
        change = calculate_percentage_change(int(counts[-1]), int(counts[0]))
        direction = "increase" if change > 0 else "decrease" if change < 0 else "stable"
        return f"{direction.capitalize()} of {abs(change):.1f}% over available period"

def calculate_percentage_change(current: float, previous: float) -> float:
    """
    Safely calculates the percentage change between current and previous values.
    """
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    return round(((current - previous) / previous) * 100, 2)
