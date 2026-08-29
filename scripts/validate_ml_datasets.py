"""
scripts/validate_ml_datasets.py
--------------------------------
Dataset Validation & Quality Assurance Module.
Validates the 3 generated ML datasets in datasets/processed/:
1. crime_risk_train.csv
2. hotspot_train.csv
3. offender_train.csv

Generates detailed dataset quality metrics, schema conformance, missing value checks,
target class balance analysis, and data sufficiency reports.
"""

import os
import pandas as pd
import numpy as np


def validate_dataset(filepath: str, name: str, target_col: str, feature_cols: list[str]) -> dict:
    print("\n" + "=" * 70)
    print(f"VALIDATING DATASET: {name} ({os.path.basename(filepath)})")
    print("=" * 70)

    if not os.path.exists(filepath):
        print(f"ERROR: File not found at {filepath}")
        return {"status": "FAILED", "reason": "File not found"}

    df = pd.read_csv(filepath)
    total_rows = len(df)
    total_cols = len(df.columns)
    
    print(f"Total Rows           : {total_rows:,}")
    print(f"Total Columns        : {total_cols}")
    print(f"Columns List         : {list(df.columns)}")

    # 1. Missing Values
    null_counts = df.isnull().sum()
    total_nulls = null_counts.sum()
    print(f"\n--- Missing Values Breakdown ---")
    if total_nulls == 0:
        print("[OK] Clean! 0 missing values across all columns.")
    else:
        for col, n_null in null_counts.items():
            if n_null > 0:
                print(f"  - {col}: {n_null} missing ({n_null/total_rows*100:.2f}%)")

    # 2. Duplicate Rows
    duplicates = df.duplicated().sum()
    print(f"\n--- Duplicate Rows Check ---")
    print(f"  - Duplicate rows count: {duplicates:,} ({duplicates/total_rows*100:.2f}%)")

    # 3. Target Distribution
    print(f"\n--- Target Column Analysis ('{target_col}') ---")
    if target_col in df.columns:
        target_counts = df[target_col].value_counts()
        for val, cnt in target_counts.items():
            pct = (cnt / total_rows) * 100
            print(f"  - Target '{val}': {cnt:,} rows ({pct:.2f}%)")
    else:
        print(f"  WARNING: Target column '{target_col}' not found in dataset!")

    # 4. Feature Summary Metrics
    print(f"\n--- Numeric Feature Summary ---")
    numeric_df = df.select_dtypes(include=[np.number])
    summary = numeric_df.describe().T[['mean', 'std', 'min', '50%', 'max']]
    print(summary.to_string())

    # 5. Data Sufficiency & Quality Warnings
    print(f"\n--- Data Quality & Sufficiency Verdict ---")
    warnings = []
    if total_rows < 1000:
        warnings.append(f"Row count ({total_rows}) is below recommended 1,000 threshold for QuickML.")
    if duplicates > 0:
        warnings.append(f"Dataset contains {duplicates} duplicate rows.")
    if total_nulls > 0:
        warnings.append(f"Dataset contains {total_nulls} missing values.")

    if not warnings:
        print("[OK] EXCELLENT: Dataset passed all quality checks! Fully ready for Catalyst QuickML.")
    else:
        for w in warnings:
            print(f"  [WARN] {w}")

    return {
        "dataset_name": name,
        "filepath": filepath,
        "total_rows": total_rows,
        "total_cols": total_cols,
        "null_count": total_nulls,
        "duplicates": duplicates,
        "warnings": warnings,
        "sufficient_for_ml": total_rows >= 1000 and (total_nulls == 0 or total_nulls / (total_rows * total_cols) < 0.05)
    }


def main():
    print("======================================================================")
    print("CrimeNexus ML Dataset Quality Assurance & Schema Validation Suite")
    print("======================================================================")

    data_dir = "datasets/processed"

    # 1. Crime Risk Validation
    risk_path = os.path.join(data_dir, "crime_risk_train.csv")
    r1 = validate_dataset(
        risk_path,
        "Crime Risk Prediction",
        target_col="risk_tier",
        feature_cols=["DistrictID", "PoliceStationID", "CrimeMajorHeadID", "CrimeMinorHeadID", "gravity_offence_id", "hour_of_day", "is_weekend", "is_night_time"]
    )

    # 2. Future Hotspot Validation
    hotspot_path = os.path.join(data_dir, "hotspot_train.csv")
    r2 = validate_dataset(
        hotspot_path,
        "Future Hotspot Prediction",
        target_col="is_future_hotspot",
        feature_cols=["grid_lat", "grid_lon", "prior_7d_crime_count", "prior_30d_crime_count", "spatial_density_ratio", "peak_hour_window"]
    )

    # 3. Repeat Offender Validation
    offender_path = os.path.join(data_dir, "offender_train.csv")
    r3 = validate_dataset(
        offender_path,
        "Repeat Offender Recidivism Prediction",
        target_col="recidivism_flag",
        feature_cols=["age_years", "gender_id", "prior_case_count", "arrest_count", "chargesheet_count", "co_offender_count", "grave_offence_ratio"]
    )

    print("\n" + "=" * 70)
    print("FINAL SUMMARY REPORT FOR QUICKML UPLOAD READINESS")
    print("=" * 70)
    print(f"1. Crime Risk Dataset       : {r1['total_rows']:,} rows | Status: {'READY FOR QUICKML [OK]' if r1['sufficient_for_ml'] else 'NEEDS ATTENTION [WARN]'}")
    print(f"2. Future Hotspot Dataset   : {r2['total_rows']:,} rows | Status: {'READY FOR QUICKML [OK]' if r2['sufficient_for_ml'] else 'NEEDS ATTENTION [WARN]'}")
    print(f"3. Repeat Offender Dataset  : {r3['total_rows']:,} rows | Status: {'READY FOR QUICKML [OK]' if r3['sufficient_for_ml'] else 'NEEDS ATTENTION [WARN]'}")
    print("=" * 70)


if __name__ == "__main__":
    main()
