import joblib
import pandas as pd

def predict_hotspot_probability(model, features):
    """
    Predict probability of a district becoming a crime hotspot.
    """
    if isinstance(model, dict) and model.get("fallback"):
        # Heuristic/Deterministic Fallback
        trend = features.get("trend_metrics", 1.0)
        prob = 0.45 * trend
        prob = min(0.95, max(0.05, prob))
        growth = features.get("historical_crime_growth", 1.0)
        if growth > 1.05:
            trend_str = "RISING"
        elif growth < 0.95:
            trend_str = "FALLING"
        else:
            trend_str = "STABLE"
        return {
            "hotspot_probability": prob,
            "trend": trend_str
        }

    if isinstance(model, str):
        model = joblib.load(model)
        
    preprocessor = model["preprocessor"]
    clf = model["model"]
    
    df = pd.DataFrame([features])
    X_processed = preprocessor.transform(df)
    
    prob = float(clf.predict_proba(X_processed)[0][1])
    
    # Calculate trend based on historical growth
    growth = features.get("historical_crime_growth", 1.0)
    if growth > 1.05:
        trend = "RISING"
    elif growth < 0.95:
        trend = "FALLING"
    else:
        trend = "STABLE"
        
    return {
        "hotspot_probability": prob,
        "trend": trend
    }

