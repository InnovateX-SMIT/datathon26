import joblib
import pandas as pd

def predict_hotspot_probability(model, features):
    """
    Predict probability of a district becoming a crime hotspot.
    
    Parameters:
    - model: Loaded dictionary containing preprocessor, model, feature_names
             or path to model pickle file.
    - features: Dict with keys 'district', 'trend_metrics', 'historical_crime_growth'.
    
    Returns:
    - Dict with 'hotspot_probability' (float) and 'trend' (str)
    """
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
