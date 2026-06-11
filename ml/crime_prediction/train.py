import os
import sqlite3
import joblib
import pandas as pd
import numpy as np
from xgboost import XGBClassifier, XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

def get_db_connection():
    paths = ["crime_intel.db", "backend/crime_intel.db", "../crime_intel.db"]
    for path in paths:
        if os.path.exists(path) and os.path.getsize(path) > 1000000:
            return sqlite3.connect(path)
    return sqlite3.connect("crime_intel.db")

def train_crime_models():
    print("Connecting to database...")
    conn = get_db_connection()
    
    # ----------------------------------------------------
    # PART 1: Crime Type Prediction (Classifier)
    # ----------------------------------------------------
    print("Loading data for Crime Type Classifier...")
    query_type = """
        SELECT 
            ce.crime_type as crime_category, 
            l.district, 
            ce.crime_date, 
            ce.crime_time
        FROM crime_events ce
        JOIN locations l ON ce.location_id == l.id
    """
    df_type = pd.read_sql_query(query_type, conn)
    print(f"Loaded {len(df_type)} crime events.")
    
    # Process temporal features
    df_type["crime_date"] = pd.to_datetime(df_type["crime_date"])
    df_type["month"] = df_type["crime_date"].dt.month
    df_type["day_of_week"] = df_type["crime_date"].dt.dayofweek
    
    def parse_hour(time_str):
        if not time_str:
            return 12
        try:
            return int(time_str.split(":")[0])
        except Exception:
            return 12
            
    df_type["hour"] = df_type["crime_time"].apply(parse_hour)
    
    # Calculate historical crime counts by district
    district_counts = df_type["district"].value_counts().to_dict()
    df_type["historical_crime_count"] = df_type["district"].map(district_counts)
    
    X_type = df_type[["district", "month", "hour", "day_of_week", "historical_crime_count"]]
    y_type_raw = df_type["crime_category"]
    
    label_encoder = LabelEncoder()
    y_type = label_encoder.fit_transform(y_type_raw)
    
    cat_features = ["district"]
    num_features = ["month", "hour", "day_of_week", "historical_crime_count"]
    
    num_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])
    cat_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="constant", fill_value="unknown")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])
    
    preprocessor_type = ColumnTransformer(
        transformers=[
            ("num", num_transformer, num_features),
            ("cat", cat_transformer, cat_features)
        ]
    )
    
    X_train_t, X_test_t, y_train_t, y_test_t = train_test_split(X_type, y_type, test_size=0.2, random_state=42)
    
    X_train_t_proc = preprocessor_type.fit_transform(X_train_t)
    X_test_t_proc = preprocessor_type.transform(X_test_t)
    
    cat_encoder = preprocessor_type.named_transformers_["cat"].named_steps["onehot"]
    encoded_cat_names = cat_encoder.get_feature_names_out(cat_features)
    feature_names_type = list(num_features) + list(encoded_cat_names)
    feature_names_type = [f.replace("[", "").replace("]", "").replace("<", "") for f in feature_names_type]
    
    print("Training Crime Type XGBClassifier...")
    clf_type = XGBClassifier(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        random_state=42,
        eval_metric="mlogloss"
    )
    clf_type.fit(X_train_t_proc, y_train_t)
    print(f"Crime Type test accuracy: {clf_type.score(X_test_t_proc, y_test_t):.4f}")
    
    print("Saving Crime Type model...")
    os.makedirs("ml/crime_prediction", exist_ok=True)
    joblib.dump({
        "preprocessor": preprocessor_type,
        "label_encoder": label_encoder,
        "model": clf_type,
        "feature_names": feature_names_type
    }, "ml/crime_prediction/model.pkl")
    
    # ----------------------------------------------------
    # PART 2: Crime Risk Scoring (Regressor)
    # ----------------------------------------------------
    print("Loading and preparing data for Crime Risk Regressor...")
    query_risk = """
        SELECT 
            ce.crime_type as crime_category, 
            l.district, 
            ce.severity,
            strftime('%Y', ce.crime_date) as year
        FROM crime_events ce
        JOIN locations l ON ce.location_id == l.id
    """
    df_risk = pd.read_sql_query(query_risk, conn)
    
    # Group by district, crime_category, and year to create a multi-row training set
    df_grouped = df_risk.groupby(["district", "crime_category", "year"]).agg(
        crime_count=("severity", "count"),
        avg_severity=("severity", "mean")
    ).reset_index()
    
    # Define target risk_score between 0 and 100
    max_count = df_grouped["crime_count"].max()
    df_grouped["risk_score"] = (df_grouped["crime_count"] / max_count) * 80 + df_grouped["avg_severity"] * 2
    df_grouped["risk_score"] = df_grouped["risk_score"].clip(0, 100)
    
    X_risk = df_grouped[["district", "crime_category", "crime_count"]]
    X_risk = X_risk.rename(columns={"crime_count": "historical_crime_count"})
    y_risk = df_grouped["risk_score"]
    
    cat_risk = ["district", "crime_category"]
    num_risk = ["historical_crime_count"]
    
    num_transformer_r = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])
    cat_transformer_r = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="constant", fill_value="unknown")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])
    
    preprocessor_risk = ColumnTransformer(
        transformers=[
            ("num", num_transformer_r, num_risk),
            ("cat", cat_transformer_r, cat_risk)
        ]
    )
    
    X_train_r, X_test_r, y_train_r, y_test_r = train_test_split(X_risk, y_risk, test_size=0.2, random_state=42)
    
    X_train_r_proc = preprocessor_risk.fit_transform(X_train_r)
    X_test_r_proc = preprocessor_risk.transform(X_test_r)
    
    cat_encoder_r = preprocessor_risk.named_transformers_["cat"].named_steps["onehot"]
    encoded_cat_names_r = cat_encoder_r.get_feature_names_out(cat_risk)
    feature_names_risk = list(num_risk) + list(encoded_cat_names_r)
    feature_names_risk = [f.replace("[", "").replace("]", "").replace("<", "") for f in feature_names_risk]
    
    print("Training Crime Risk XGBRegressor...")
    reg_risk = XGBRegressor(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        random_state=42
    )
    reg_risk.fit(X_train_r_proc, y_train_r)
    
    # Evaluate R^2
    r2 = reg_risk.score(X_test_r_proc, y_test_r)
    print(f"Crime Risk test R^2 score: {r2:.4f}")
    
    print("Saving Crime Risk model...")
    joblib.dump({
        "preprocessor": preprocessor_risk,
        "model": reg_risk,
        "feature_names": feature_names_risk
    }, "ml/crime_prediction/risk_model.pkl")
    
    conn.close()
    print("All crime prediction models trained and saved successfully.")

if __name__ == "__main__":
    train_crime_models()
