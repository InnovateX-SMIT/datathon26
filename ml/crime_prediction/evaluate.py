from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, f1_score

def evaluate_crime_type_prediction(predictions, ground_truth):
    """
    Evaluate crime type classifier performance.
    
    Parameters:
    - predictions: Predicted labels.
    - ground_truth: True labels.
    
    Returns:
    - Dict of metrics.
    """
    return {
        "accuracy": float(accuracy_score(ground_truth, predictions)),
        "f1_macro": float(f1_score(ground_truth, predictions, average="macro", zero_division=0))
    }

def evaluate_crime_risk_scoring(predictions, ground_truth):
    """
    Evaluate crime risk regressor performance.
    
    Parameters:
    - predictions: Predicted risk scores.
    - ground_truth: True risk scores.
    
    Returns:
    - Dict of metrics.
    """
    return {
        "mse": float(mean_squared_error(ground_truth, predictions)),
        "r2": float(r2_score(ground_truth, predictions))
    }
