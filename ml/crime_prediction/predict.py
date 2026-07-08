import joblib
import pandas as pd
import numpy as np

def predict_crime_category(model, features):
    """
    Predict likely future crime category.
    """
    if isinstance(model, dict) and model.get("fallback"):
        # Heuristic/Deterministic Fallback
        hour = features.get("hour", 12)
        if hour >= 22 or hour < 4:
            crime_type = "Theft"
            confidence = 0.72
        else:
            crime_type = "Public Nuisance"
            confidence = 0.58
        return {
            "crime_type": crime_type,
            "confidence": confidence
        }

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
    """
    if isinstance(model, dict) and model.get("fallback"):
        # Heuristic/Deterministic Fallback
        count = features.get("historical_crime_count", 10)
        score = float(count * 1.6)
        score = max(5.0, min(95.0, score))
        risk_level = "LOW" if score <= 39 else ("MEDIUM" if score <= 69 else "HIGH")
        return {
            "risk_score": score,
            "risk_level": risk_level
        }

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

