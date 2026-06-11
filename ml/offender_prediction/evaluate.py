from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

def evaluate_offender_prediction(predictions, ground_truth):
    """
    Compute metrics: F1, ROC, Accuracy, Precision, Recall.
    
    Parameters:
    - predictions: List/array of predicted probabilities or labels.
    - ground_truth: List/array of target labels.
    
    Returns:
    - Dictionary containing evaluation metrics.
    """
    # Assuming predictions are probabilities, let's threshold at 0.5 for class predictions
    pred_labels = [1 if p > 0.5 else 0 for p in predictions]
    
    metrics = {
        "accuracy": float(accuracy_score(ground_truth, pred_labels)),
        "precision": float(precision_score(ground_truth, pred_labels, zero_division=0)),
        "recall": float(recall_score(ground_truth, pred_labels, zero_division=0)),
        "f1": float(f1_score(ground_truth, pred_labels, zero_division=0)),
    }
    
    try:
        metrics["roc_auc"] = float(roc_auc_score(ground_truth, predictions))
    except ValueError:
        metrics["roc_auc"] = 0.5
        
    return metrics
