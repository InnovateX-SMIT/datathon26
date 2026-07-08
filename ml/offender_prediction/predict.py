import joblib
import pandas as pd
import numpy as np

def predict_offender_recidivism(model, suspect_features):
    """
    Score suspect profiles.
    """
    if isinstance(model, dict) and model.get("fallback"):
        # Heuristic/Deterministic Fallback
        age = suspect_features.get("age", 30)
        caste = suspect_features.get("caste", "General")
        prob = 0.2
        if age < 25:
            prob += 0.35
        elif age > 50:
            prob -= 0.1
        if caste in ["SC", "ST"]:
            prob += 0.08
        prob = min(0.95, max(0.05, prob))
        risk_level = "LOW" if prob <= 0.39 else ("MEDIUM" if prob <= 0.69 else "HIGH")
        return {
            "probability": prob,
            "risk_level": risk_level
        }

    if isinstance(model, str):
        model = joblib.load(model)
        
    preprocessor = model["preprocessor"]
    clf = model["model"]
    
    # Format inputs into DataFrame
    df = pd.DataFrame([suspect_features])
    
    # Transform features
    X_processed = preprocessor.transform(df)
    
    # Predict probability
    prob = float(clf.predict_proba(X_processed)[0][1])
    
    # Assign risk levels:
    # 0-39 Low, 40-69 Medium, 70-100 High
    score = int(round(prob * 100))
    if score <= 39:
        risk_level = "LOW"
    elif score <= 69:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"
        
    return {
        "probability": prob,
        "risk_level": risk_level
    }

