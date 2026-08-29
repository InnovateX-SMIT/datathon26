"""
scripts/generate_ml_datasets.py
--------------------------------
Generates processed ML training datasets from SQLite backend/crime_intel.db.
Outputs:
- datasets/processed/crime_risk_train.csv
- datasets/processed/hotspot_train.csv
- datasets/processed/offender_train.csv
"""

import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ml.feature_extractor import (
    get_db_connection,
    extract_crime_risk_features,
    extract_hotspot_features,
    extract_offender_features,
)


def main():
    print("=" * 70)
    print("CrimeNexus ML Dataset Generator — Phase 5 Intelligence")
    print("=" * 70)

    db_path = "backend/crime_intel.db"
    out_dir = "datasets/processed"
    os.makedirs(out_dir, exist_ok=True)

    print(f"Connecting to database: {db_path}...")
    conn = get_db_connection(db_path)

    # 1. Crime Risk Dataset
    print("\n[1/3] Extracting Crime Risk Prediction features...")
    df_risk = extract_crime_risk_features(conn)
    risk_out = os.path.join(out_dir, "crime_risk_train.csv")
    df_risk.to_csv(risk_out, index=False)
    print(f"  --> Saved: {risk_out} ({len(df_risk):,} rows, {len(df_risk.columns)} columns)")

    # 2. Future Hotspot Dataset
    print("\n[2/3] Extracting Future Hotspot Prediction features...")
    df_hotspot = extract_hotspot_features(conn)
    hotspot_out = os.path.join(out_dir, "hotspot_train.csv")
    df_hotspot.to_csv(hotspot_out, index=False)
    print(f"  --> Saved: {hotspot_out} ({len(df_hotspot):,} rows, {len(df_hotspot.columns)} columns)")

    # 3. Repeat Offender Dataset
    print("\n[3/3] Extracting Repeat Offender Recidivism features...")
    df_offender = extract_offender_features(conn)
    offender_out = os.path.join(out_dir, "offender_train.csv")
    df_offender.to_csv(offender_out, index=False)
    print(f"  --> Saved: {offender_out} ({len(df_offender):,} rows, {len(df_offender.columns)} columns)")

    conn.close()

    print("\n" + "=" * 70)
    print("SUCCESS: All 3 ML training datasets generated successfully!")
    print("Target Destination: datasets/processed/")
    print("These CSV files are ready to be uploaded to Zoho Catalyst QuickML!")
    print("=" * 70)


if __name__ == "__main__":
    main()
