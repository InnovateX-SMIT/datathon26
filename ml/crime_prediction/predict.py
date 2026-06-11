import joblib
import pandas as pd
import numpy as np

def predict_crime_category(model, features):
    """
    Predict likely future crime category.
    
    Parameters:
    - model: Loaded dictionary containing preprocessor, label_encoder, model, etc.
             or path to model pickle file.
    - features: Dict with keys 'district', 'month', 'hour', 'day_of_week', 'historical_crime_count'.
    
    Returns:
    - Dict with 'crime_type' (str) and 'confidence' (float)
    """
    if isinstance(model, str):
        model = joblib.load(model)
        
    preprocessor = model["preprocessor"]
    label_encoder = model["label_encoder"]
    clf = model["model"]
    
    df = pd.DataFrame([features])
    X_processed = preprocessor.transform(df)
    
    # Predict probabilities
    probs = clf.predict_proba(X_processed)[0]
    best_idx = np.argmax(probs)
    
    crime_type = label_encoder.inverse_transform([best_idx])[0]
    confidence = float(probs[best_idx])
    
    return {
        "crime_type": str(crime_type),
        "confidence": confidence
    }

def predict_crime_risk_score(model, features):
    """
    Predict risk level of crime occurrence.
    
    Parameters:
    - model: Loaded dictionary containing preprocessor, model, etc.
             or path to model pickle file.
    - features: Dict with keys 'district', 'crime_category', 'historical_crime_count'.
    
    Returns:
    - Dict with 'risk_score' (float) and 'risk_level' (str)
    """
    if isinstance(model, str):
        model = joblib.load(model)
        
    preprocessor = model["preprocessor"]
    reg = model["model"]
    
    df = pd.DataFrame([features])
    X_processed = preprocessor.transform(df)
    
    # Predict score
    score = float(reg.predict(X_processed)[0])
    score = max(0.0, min(100.0, score))
    
    # Define risk levels:
    # 0-39 Low, 40-69 Medium, 70-100 High
    rounded_score = int(round(score))
    if rounded_score <= 39:
        risk_level = "LOW"
    elif rounded_score <= 69:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"
        
    return {
        "risk_score": score,
        "risk_level": risk_level
    }
