import joblib
import pandas as pd
import numpy as np

def predict_offender_recidivism(model, suspect_features):
    """
    Score suspect profiles.
    
    Parameters:
    - model: Loaded dictionary containing 'preprocessor', 'model', and 'feature_names', 
             or path to model pickle file.
    - suspect_features: Dictionary with keys 'age', 'occupation', 'caste', 'district'.
    
    Returns:
    - Dict with 'probability' (float) and 'risk_level' (str)
    """
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
