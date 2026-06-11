import os
import sqlite3
import joblib
import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

def get_db_connection():
    paths = ["crime_intel.db", "backend/crime_intel.db", "../crime_intel.db"]
    for path in paths:
        if os.path.exists(path) and os.path.getsize(path) > 1000000:
            return sqlite3.connect(path)
    return sqlite3.connect("crime_intel.db")

def train_offender_model():
    print("Connecting to database...")
    conn = get_db_connection()
    
    query = """
        SELECT 
            c.age, 
            c.occupation, 
            c.caste, 
            l.district,
            c.risk_score
        FROM criminals c
        JOIN crime_participation cp ON c.id = cp.criminal_id
        JOIN crime_events ce ON cp.crime_event_id = ce.id
        JOIN locations l ON ce.location_id = l.id
    """
    
    print("Loading data...")
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    print(f"Loaded {len(df)} offender profiles.")
    
    # Target label: risk_score > 0.5 (which maps to 0.85 in seeded DB for repeat offenders)
    X = df[["age", "occupation", "caste", "district"]]
    y = (df["risk_score"] > 0.5).astype(int)
    
    # Define preprocessor
    num_features = ["age"]
    cat_features = ["occupation", "caste", "district"]
    
    num_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])
    
    cat_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="constant", fill_value="unknown")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", num_transformer, num_features),
            ("cat", cat_transformer, cat_features)
        ]
    )
    
    print("Splitting datasets...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Preprocessing features...")
    X_train_processed = preprocessor.fit_transform(X_train)
    X_test_processed = preprocessor.transform(X_test)
    
    # Get feature names after one-hot encoding
    cat_encoder = preprocessor.named_transformers_["cat"].named_steps["onehot"]
    encoded_cat_names = cat_encoder.get_feature_names_out(cat_features)
    feature_names = list(num_features) + list(encoded_cat_names)
    
    # Clean feature names (remove special characters for XGBoost if needed)
    feature_names = [f.replace("[", "").replace("]", "").replace("<", "") for f in feature_names]
    
    print("Training XGBoost Classifier...")
    model = XGBClassifier(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        random_state=42,
        eval_metric="logloss"
    )
    model.fit(X_train_processed, y_train)
    
    accuracy = model.score(X_test_processed, y_test)
    print(f"Model test accuracy: {accuracy:.4f}")
    
    print("Saving model to ml/offender_prediction/model.pkl...")
    os.makedirs("ml/offender_prediction", exist_ok=True)
    joblib.dump({
        "preprocessor": preprocessor,
        "model": model,
        "feature_names": feature_names
    }, "ml/offender_prediction/model.pkl")
    
    print("Model trained and saved successfully.")

if __name__ == "__main__":
    train_offender_model()
