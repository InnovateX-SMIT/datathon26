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

def train_hotspot_model():
    print("Connecting to database...")
    conn = get_db_connection()
    
    query = """
        SELECT 
            ce.id,
            l.district,
            strftime('%Y-%m', ce.crime_date) as year_month
        FROM crime_events ce
        JOIN locations l ON ce.location_id == l.id
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    print("Aggregating monthly crime counts by district...")
    # Group by district and year_month
    agg_df = df.groupby(["district", "year_month"]).size().reset_index(name="crime_count")
    
    # Sort to compute lag features correctly
    agg_df = agg_df.sort_values(by=["district", "year_month"]).reset_index(drop=True)
    
    # Compute lagged crime counts to define growth
    agg_df["prev_crime_count"] = agg_df.groupby("district")["crime_count"].shift(1)
    
    # Fill NaN values for the first month in history
    agg_df["prev_crime_count"] = agg_df["prev_crime_count"].fillna(agg_df["crime_count"])
    
    # Calculate historical crime growth: current count / prev count
    agg_df["historical_crime_growth"] = (agg_df["crime_count"] + 1) / (agg_df["prev_crime_count"] + 1)
    
    # Define trend metrics as the absolute count of the previous period
    agg_df["trend_metrics"] = agg_df["prev_crime_count"]
    
    # Hotspot label: Top 30% highest crime counts in a given district-month
    threshold = agg_df["crime_count"].quantile(0.70)
    agg_df["is_hotspot"] = (agg_df["crime_count"] >= threshold).astype(int)
    
    # Select features & target
    X = agg_df[["district", "trend_metrics", "historical_crime_growth"]]
    y = agg_df["is_hotspot"]
    
    cat_features = ["district"]
    num_features = ["trend_metrics", "historical_crime_growth"]
    
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
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    X_train_proc = preprocessor.fit_transform(X_train)
    X_test_proc = preprocessor.transform(X_test)
    
    cat_encoder = preprocessor.named_transformers_["cat"].named_steps["onehot"]
    encoded_cat_names = cat_encoder.get_feature_names_out(cat_features)
    feature_names = list(num_features) + list(encoded_cat_names)
    feature_names = [f.replace("[", "").replace("]", "").replace("<", "") for f in feature_names]
    
    print("Training Hotspot XGBClassifier...")
    model = XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        random_state=42,
        eval_metric="logloss"
    )
    model.fit(X_train_proc, y_train)
    
    accuracy = model.score(X_test_proc, y_test)
    print(f"Hotspot model test accuracy: {accuracy:.4f}")
    
    print("Saving hotspot model to ml/hotspot_prediction/model.pkl...")
    os.makedirs("ml/hotspot_prediction", exist_ok=True)
    joblib.dump({
        "preprocessor": preprocessor,
        "model": model,
        "feature_names": feature_names
    }, "ml/hotspot_prediction/model.pkl")
    
    print("Hotspot model trained successfully.")

if __name__ == "__main__":
    train_hotspot_model()
