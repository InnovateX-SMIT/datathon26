import shap
import pandas as pd
import numpy as np

def compute_shap_explanations(model, data, feature_names):
    """
    Compute SHAP values for tree-based models and map them back to feature names.
    
    Parameters:
    - model: The trained XGBoost or scikit-learn model.
    - data: A 2D numpy array or pandas DataFrame representing the preprocessed features of a single sample.
    - feature_names: List of strings matching the columns of the preprocessed features.
    
    Returns:
    - List of dictionaries with keys 'feature' and 'impact'.
    """
    # Create the explainer
    explainer = shap.TreeExplainer(model)
    
    # Calculate SHAP values
    shap_vals = explainer.shap_values(data)
    
    # Handle different shape structures returned by SHAP for classifiers/regressors
    if isinstance(shap_vals, list):
        # Multi-class or binary classification lists: choose class 1 if binary
        shap_vals = shap_vals[1] if len(shap_vals) > 1 else shap_vals[0]
    elif isinstance(shap_vals, np.ndarray) and len(shap_vals.shape) == 3:
        # Multi-class 3D array: [samples, features, classes]
        shap_vals = shap_vals[:, :, 1] if shap_vals.shape[2] > 1 else shap_vals[:, :, 0]
    
    # If shap_vals is a tuple or has multiple dimensions
    if isinstance(shap_vals, np.ndarray) and len(shap_vals.shape) > 1:
        # Extract the first sample
        shap_vals = shap_vals[0]
    
    # Map back to feature names
    results = []
    for name, val in zip(feature_names, shap_vals):
        results.append({
            "feature": name,
            "impact": float(val)
        })
    
    # Sort by absolute impact descending
    results = sorted(results, key=lambda x: abs(x["impact"]), reverse=True)
    return results
