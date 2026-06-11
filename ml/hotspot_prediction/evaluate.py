from sklearn.metrics import accuracy_score, f1_score

def evaluate_hotspot_prediction(predictions, ground_truth):
    """
    Compute accuracy and F1 score for hotspot classifier predictions.
    
    Parameters:
    - predictions: List/array of predicted probabilities or labels.
    - ground_truth: List/array of target labels.
    
    Returns:
    - Dictionary containing evaluation metrics.
    """
    pred_labels = [1 if p > 0.5 else 0 for p in predictions]
    
    return {
        "accuracy": float(accuracy_score(ground_truth, pred_labels)),
        "f1": float(f1_score(ground_truth, pred_labels, zero_division=0))
    }
