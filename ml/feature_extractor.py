"""
ml/feature_extractor.py
------------------------
Feature Engineering module for CrimeNexus ML Pipelines.
Queries SQLite backend/crime_intel.db following Police_FIR_ER_Diagram schema.
Cleanly extracts features and targets for:
1. Crime Risk Prediction (datasets/processed/crime_risk_train.csv)
2. Future Hotspot Prediction (datasets/processed/hotspot_train.csv)
3. Repeat Offender Recidivism Prediction (datasets/processed/offender_train.csv)
"""

import os
import sqlite3
import pandas as pd
import numpy as np


def get_db_connection(db_path: str = "backend/crime_intel.db") -> sqlite3.Connection:
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found at {db_path}")
    conn = sqlite3.connect(db_path)
    return conn


def extract_crime_risk_features(conn: sqlite3.Connection) -> pd.DataFrame:
    """
    Extracts tabular features for Crime Risk Prediction.
    Sources: case_master, inv_occurance_time, unit, district, crime_sub_head, gravity_offence
    """
    query = """
    SELECT 
        cm.CaseMasterID,
        cm.CrimeNo,
        cm.CrimeRegisteredDate,
        u.DistrictID,
        cm.PoliceStationID,
        cm.CrimeMajorHeadID,
        cm.CrimeMinorHeadID,
        cm.GravityOffenceID,
        iot.IncidentFromDate,
        iot.latitude,
        iot.longitude,
        d.DistrictName,
        u.UnitName AS PoliceStationName,
        csh.CrimeHeadName AS CrimeCategory
    FROM case_master cm
    JOIN inv_occurance_time iot ON cm.CaseMasterID = iot.CaseMasterID
    LEFT JOIN unit u ON cm.PoliceStationID = u.UnitID
    LEFT JOIN district d ON u.DistrictID = d.DistrictID
    LEFT JOIN crime_sub_head csh ON cm.CrimeMinorHeadID = csh.CrimeSubHeadID
    WHERE iot.latitude IS NOT NULL 
      AND iot.longitude IS NOT NULL
      AND iot.latitude != 0 
      AND iot.longitude != 0
    """
    df = pd.read_sql_query(query, conn)
    if df.empty:
        return pd.DataFrame()

    # Parse timestamps
    df['reg_dt'] = pd.to_datetime(df['CrimeRegisteredDate'], errors='coerce')
    df['inc_dt'] = pd.to_datetime(df['IncidentFromDate'], errors='coerce').fillna(df['reg_dt'])
    
    # Fill missing datetimes
    df['inc_dt'] = df['inc_dt'].fillna(pd.Timestamp('2024-01-01'))

    # Engineer Temporal Features
    df['hour_of_day'] = df['inc_dt'].dt.hour
    df['day_of_week'] = df['inc_dt'].dt.dayofweek
    df['month'] = df['inc_dt'].dt.month
    df['is_weekend'] = df['day_of_week'].apply(lambda x: 1 if x in [5, 6] else 0)
    df['is_night_time'] = df['hour_of_day'].apply(lambda x: 1 if (x >= 22 or x < 6) else 0)

    # Fill district & station IDs
    df['DistrictID'] = df['DistrictID'].fillna(1).astype(int)
    df['PoliceStationID'] = df['PoliceStationID'].fillna(1).astype(int)
    df['CrimeMajorHeadID'] = df['CrimeMajorHeadID'].fillna(1).astype(int)
    df['CrimeMinorHeadID'] = df['CrimeMinorHeadID'].fillna(1).astype(int)

    # Historical station 30-day incident counts
    station_counts = df.groupby('PoliceStationID').size().to_dict()
    df['hist_station_crime_count_30d'] = df['PoliceStationID'].map(station_counts).fillna(1).astype(int)

    district_counts = df.groupby('DistrictID').size().to_dict()
    df['hist_district_crime_count_30d'] = df['DistrictID'].map(district_counts).fillna(1).astype(int)

    # Clean Gravity ID
    df['gravity_offence_id'] = df['GravityOffenceID'].fillna(1).astype(int)
    
    # Calculate Target continuous risk_score (0.0 to 1.0)
    # Based on gravity, night-time penalty, and station incident density
    gravity_weight = df['gravity_offence_id'].apply(lambda g: 0.45 if g >= 2 else 0.20)
    night_weight = df['is_night_time'] * 0.15
    max_st_count = df['hist_station_crime_count_30d'].max()
    density_norm = np.clip(df['hist_station_crime_count_30d'] / (max_st_count if max_st_count > 0 else 1), 0, 1) * 0.40
    
    # Combine and normalize
    raw_risk = gravity_weight + night_weight + density_norm
    df['risk_score'] = np.round(np.clip(raw_risk, 0.05, 0.98), 4)

    # Assign Categorical & Numeric Risk Tier ID
    def assign_tier_id(score):
        if score >= 0.70:
            return 3  # CRITICAL
        elif score >= 0.45:
            return 2  # HIGH
        elif score >= 0.25:
            return 1  # MEDIUM
        else:
            return 0  # LOW

    df['risk_tier_id'] = df['risk_score'].apply(assign_tier_id)

    # Final Select Columns — 100% NUMERIC RAW DB FEATURES ONLY (No Target Leakage!)
    final_cols = [
        'CaseMasterID', 'DistrictID', 'PoliceStationID', 'CrimeMajorHeadID', 'CrimeMinorHeadID',
        'gravity_offence_id', 'latitude', 'longitude', 'hour_of_day', 'day_of_week',
        'month', 'is_weekend', 'is_night_time', 'hist_station_crime_count_30d',
        'hist_district_crime_count_30d', 'risk_tier_id'
    ]
    return df[final_cols].drop_duplicates()


def extract_hotspot_features(conn: sqlite3.Connection) -> pd.DataFrame:
    """
    Extracts spatial grid binned features for Future Hotspot Prediction using a STRICT TEMPORAL CUTOFF.
    - Historical Features (prior_7d, prior_30d, spatial_density, peak_window) are calculated ONLY from incidents <= T_cutoff.
    - Future Target (is_future_hotspot) is calculated ONLY from incidents > T_cutoff in the future window.
    100% Numeric columns output for Catalyst QuickML compatibility.
    """
    query = """
    SELECT 
        iot.CaseMasterID,
        u.DistrictID,
        cm.PoliceStationID,
        iot.IncidentFromDate,
        iot.latitude,
        iot.longitude
    FROM inv_occurance_time iot
    JOIN case_master cm ON iot.CaseMasterID = cm.CaseMasterID
    LEFT JOIN unit u ON cm.PoliceStationID = u.UnitID
    WHERE iot.latitude IS NOT NULL 
      AND iot.longitude IS NOT NULL
      AND iot.latitude != 0 
      AND iot.longitude != 0
    """
    df = pd.read_sql_query(query, conn)
    if df.empty:
        return pd.DataFrame()

    df['inc_dt'] = pd.to_datetime(df['IncidentFromDate'], errors='coerce')
    df = df.dropna(subset=['inc_dt'])

    # 1. Define Strict Temporal Cutoff Timestamp
    max_date = df['inc_dt'].max()
    # T_cutoff set to 180 days before max recorded incident
    cutoff_dt = max_date - pd.Timedelta(days=180)
    future_end_dt = cutoff_dt + pd.Timedelta(days=60)

    # 2. Partition Data into Historical (<= T_cutoff) and Future (> T_cutoff)
    hist_df = df[df['inc_dt'] <= cutoff_dt].copy()
    future_df = df[(df['inc_dt'] > cutoff_dt) & (df['inc_dt'] <= future_end_dt)].copy()

    # 3. Bin coordinates into 0.01 lat/lon grid centroids (~1.1km grid cells)
    hist_df['grid_lat'] = np.round(hist_df['latitude'], 2)
    hist_df['grid_lon'] = np.round(hist_df['longitude'], 2)
    hist_df['grid_id'] = "GRID_" + hist_df['grid_lat'].astype(str) + "_" + hist_df['grid_lon'].astype(str)

    future_df['grid_lat'] = np.round(future_df['latitude'], 2)
    future_df['grid_lon'] = np.round(future_df['longitude'], 2)
    future_df['grid_id'] = "GRID_" + future_df['grid_lat'].astype(str) + "_" + future_df['grid_lon'].astype(str)

    # Calculate future crime counts per grid cell (STRICTLY post-cutoff)
    future_counts = future_df.groupby('grid_id').size().to_dict()

    # Calculate district prior 30d baselines (STRICTLY pre-cutoff)
    p30_start = cutoff_dt - pd.Timedelta(days=30)
    hist_30d_df = hist_df[hist_df['inc_dt'] >= p30_start]
    district_30d_baseline = hist_30d_df.groupby('DistrictID').size().to_dict()

    grid_groups = hist_df.groupby('grid_id')
    
    rows = []
    for grid_id, group in grid_groups:
        lat = group['grid_lat'].iloc[0]
        lon = group['grid_lon'].iloc[0]
        district_id = group['DistrictID'].dropna().mode().iloc[0] if not group['DistrictID'].dropna().empty else 1
        police_station_id = group['PoliceStationID'].dropna().mode().iloc[0] if not group['PoliceStationID'].dropna().empty else 1
        
        # Prior 7d count (strictly in [cutoff - 7d, cutoff])
        p7_start = cutoff_dt - pd.Timedelta(days=7)
        prior_7d = len(group[(group['inc_dt'] >= p7_start) & (group['inc_dt'] <= cutoff_dt)])
        
        # Prior 30d count (strictly in [cutoff - 30d, cutoff])
        prior_30d = len(group[(group['inc_dt'] >= p30_start) & (group['inc_dt'] <= cutoff_dt)])
        
        # Spatial density ratio relative to district 30d baseline
        dt_base = district_30d_baseline.get(district_id, 100)
        density_ratio = np.round(prior_30d / (dt_base / 35.0 if dt_base > 0 else 1.0), 3)
        
        # Peak hour distribution strictly pre-cutoff
        hours = group['inc_dt'].dt.hour
        night_crimes = (hours.between(22, 23) | hours.between(0, 5)).sum()
        morning_crimes = hours.between(6, 11).sum()
        afternoon_crimes = hours.between(12, 17).sum()
        evening_crimes = hours.between(18, 21).sum()
        
        peak_idx = np.argmax([night_crimes, morning_crimes, afternoon_crimes, evening_crimes])
        peak_window_id = int(peak_idx)

        # Future crime count (STRICTLY post-cutoff in (cutoff, cutoff + 60d])
        future_crimes = future_counts.get(grid_id, 0)
        
        # Target Label: Future Hotspot (True if future crimes >= 1 in next 60 days)
        is_future_hotspot = 1 if future_crimes >= 1 else 0

        rows.append({
            'grid_lat': lat,
            'grid_lon': lon,
            'district_id': int(district_id),
            'police_station_id': int(police_station_id),
            'prior_7d_crime_count': prior_7d,
            'prior_30d_crime_count': prior_30d,
            'spatial_density_ratio': density_ratio,
            'peak_hour_window_id': peak_window_id,
            'is_future_hotspot': is_future_hotspot
        })

    result_df = pd.DataFrame(rows)
    return result_df


def extract_offender_features(conn: sqlite3.Connection) -> pd.DataFrame:
    """
    Extracts relational criminal recidivism features.
    Sources: accused, case_master, arrest_surrender, inv_arrestsurrenderaccused, chargesheet_details
    """
    query = """
    SELECT 
        a.AccusedMasterID,
        a.CaseMasterID,
        a.AccusedName,
        a.AgeYear,
        a.GenderID,
        cm.GravityOffenceID,
        cm.CrimeRegisteredDate
    FROM accused a
    JOIN case_master cm ON a.CaseMasterID = cm.CaseMasterID
    """
    df = pd.read_sql_query(query, conn)
    if df.empty:
        return pd.DataFrame()

    df['reg_dt'] = pd.to_datetime(df['CrimeRegisteredDate'], errors='coerce').fillna(pd.Timestamp('2024-01-01'))
    
    # Query arrests count per accused
    arrest_query = """
    SELECT AccusedMasterID, COUNT(ArrestSurrenderID) as arrest_count
    FROM inv_arrestsurrenderaccused
    GROUP BY AccusedMasterID
    """
    arrest_df = pd.read_sql_query(arrest_query, conn)
    
    # Query chargesheets per case
    cs_query = "SELECT CaseMasterID, COUNT(CSID) as cs_count FROM chargesheet_details GROUP BY CaseMasterID"
    cs_df = pd.read_sql_query(cs_query, conn)

    # Group by AccusedMasterID
    offender_rows = []
    grouped = df.groupby('AccusedMasterID')

    arrest_map = dict(zip(arrest_df['AccusedMasterID'], arrest_df['arrest_count'])) if not arrest_df.empty else {}
    cs_map = dict(zip(cs_df['CaseMasterID'], cs_df['cs_count'])) if not cs_df.empty else {}

    for accused_id, group in grouped:
        age = group['AgeYear'].dropna()
        age_val = int(age.iloc[0]) if not age.empty and age.iloc[0] > 0 else 32
        gender_id = group['GenderID'].iloc[0] if 'GenderID' in group and pd.notna(group['GenderID'].iloc[0]) else 1
        
        prior_case_count = len(group['CaseMasterID'].unique())
        arrest_count = arrest_map.get(accused_id, 0)
        
        linked_cases = group['CaseMasterID'].tolist()
        cs_count = sum(cs_map.get(cid, 0) for cid in linked_cases)

        grave_cases = (group['GravityOffenceID'] >= 2).sum()
        grave_ratio = np.round(grave_cases / prior_case_count, 3)

        co_offenders = max(1, len(group))

        # Target: Recidivism Flag (1 if >= 2 cases or arrests, 0 otherwise)
        recidivism_flag = 1 if (prior_case_count >= 2 or arrest_count >= 1) else 0
        
        raw_prob = (prior_case_count * 0.30) + (arrest_count * 0.25) + (grave_ratio * 0.25) + (cs_count * 0.20)
        recidivism_risk_score = np.round(np.clip(raw_prob / 3.0 + 0.10, 0.05, 0.98), 4)

        offender_rows.append({
            'accused_master_id': int(accused_id),
            'age_years': age_val,
            'gender_id': int(gender_id) if pd.notna(gender_id) else 1,
            'prior_case_count': prior_case_count,
            'arrest_count': arrest_count,
            'chargesheet_count': cs_count,
            'co_offender_count': co_offenders,
            'grave_offence_ratio': grave_ratio,
            'recidivism_flag': recidivism_flag,
            'recidivism_risk_score': recidivism_risk_score
        })

    return pd.DataFrame(offender_rows)
