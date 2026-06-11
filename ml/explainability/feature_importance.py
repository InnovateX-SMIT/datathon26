def get_gini_importance(model, feature_names):
    """
    Extract tree-based Gini feature importances from a model.
    
    Parameters:
    - model: The trained tree model.
    - feature_names: The names of the preprocessed features.
    
    Returns:
    - Sorted list of dicts with 'feature' and 'importance'.
    """
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
        results = [
            {"feature": name, "importance": float(imp)} 
            for name, imp in zip(feature_names, importances)
        ]
        return sorted(results, key=lambda x: x["importance"], reverse=True)
    return []
