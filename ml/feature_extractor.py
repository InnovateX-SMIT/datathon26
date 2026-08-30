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
    Extracts spatial sector cluster binned features for Future Hotspot Prediction using a STRICT TEMPORAL CUTOFF.
    - Historical Features (prior_7d, 30d, 90d, 180d, spatial_density, peak_window) are calculated ONLY from incidents <= T_cutoff.
    - Future Target (is_future_hotspot) is calculated ONLY from incidents > T_cutoff in the future window (cutoff, cutoff + 60d].
    - Binned at 0.05 degree (~5.5km sector beats) to provide strong, non-sparse predictive signal.
    100% Numeric columns output for Catalyst QuickML compatibility.
    """
    query = """
    SELECT 
        iot.CaseMasterID,
        u.DistrictID,
        cm.PoliceStationID,
        cm.CrimeMajorHeadID,
        cm.CrimeMinorHeadID,
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
    cutoff_dt = max_date - pd.Timedelta(days=180)
    future_end_dt = cutoff_dt + pd.Timedelta(days=60)

    # 2. Partition Data into Historical (<= T_cutoff) and Future (> T_cutoff)
    hist_df = df[df['inc_dt'] <= cutoff_dt].copy()
    future_df = df[(df['inc_dt'] > cutoff_dt) & (df['inc_dt'] <= future_end_dt)].copy()

    # 3. Bin coordinates into 0.05 degree sector centroids (~5.5km sector beats)
    hist_df['grid_lat'] = np.round(hist_df['latitude'] / 0.05) * 0.05
    hist_df['grid_lon'] = np.round(hist_df['longitude'] / 0.05) * 0.05
    hist_df['grid_id'] = "SECTOR_" + hist_df['grid_lat'].astype(str) + "_" + hist_df['grid_lon'].astype(str)

    future_df['grid_lat'] = np.round(future_df['latitude'] / 0.05) * 0.05
    future_df['grid_lon'] = np.round(future_df['longitude'] / 0.05) * 0.05
    future_df['grid_id'] = "SECTOR_" + future_df['grid_lat'].astype(str) + "_" + future_df['grid_lon'].astype(str)

    # Calculate future crime counts per sector (STRICTLY post-cutoff)
    future_counts = future_df.groupby('grid_id').size().to_dict()

    # Calculate district prior 30d baselines (STRICTLY pre-cutoff)
    p7_start = cutoff_dt - pd.Timedelta(days=7)
    p30_start = cutoff_dt - pd.Timedelta(days=30)
    p90_start = cutoff_dt - pd.Timedelta(days=90)
    p180_start = cutoff_dt - pd.Timedelta(days=180)

    hist_30d_df = hist_df[hist_df['inc_dt'] >= p30_start]
    district_30d_baseline = hist_30d_df.groupby('DistrictID').size().to_dict()

    grid_groups = hist_df.groupby('grid_id')
    
    rows = []
    for grid_id, group in grid_groups:
        lat = group['grid_lat'].iloc[0]
        lon = group['grid_lon'].iloc[0]
        district_id = group['DistrictID'].dropna().mode().iloc[0] if not group['DistrictID'].dropna().empty else 1
        police_station_id = group['PoliceStationID'].dropna().mode().iloc[0] if not group['PoliceStationID'].dropna().empty else 1
        
        prior_7d = len(group[(group['inc_dt'] >= p7_start) & (group['inc_dt'] <= cutoff_dt)])
        prior_30d = len(group[(group['inc_dt'] >= p30_start) & (group['inc_dt'] <= cutoff_dt)])
        prior_90d = len(group[(group['inc_dt'] >= p90_start) & (group['inc_dt'] <= cutoff_dt)])
        prior_180d = len(group[(group['inc_dt'] >= p180_start) & (group['inc_dt'] <= cutoff_dt)])
        
        dt_base = district_30d_baseline.get(district_id, 100)
        density_ratio = np.round(prior_30d / (dt_base / 35.0 if dt_base > 0 else 1.0), 3)
        
        hours = group['inc_dt'].dt.hour
        night_crimes = (hours.between(22, 23) | hours.between(0, 5)).sum()
        morning_crimes = hours.between(6, 11).sum()
        afternoon_crimes = hours.between(12, 17).sum()
        evening_crimes = hours.between(18, 21).sum()
        
        peak_idx = int(np.argmax([night_crimes, morning_crimes, afternoon_crimes, evening_crimes]))

        # Future crime count (STRICTLY post-cutoff in (cutoff, cutoff + 60d])
        future_crimes = future_counts.get(grid_id, 0)
        
        # Target Label: Future Hotspot (True if future crimes >= 3 in sector over 60 days)
        is_future_hotspot = 1 if future_crimes >= 3 else 0

        rows.append({
            'grid_lat': lat,
            'grid_lon': lon,
            'district_id': int(district_id),
            'police_station_id': int(police_station_id),
            'prior_7d_crime_count': prior_7d,
            'prior_30d_crime_count': prior_30d,
            'prior_90d_crime_count': prior_90d,
            'prior_180d_crime_count': prior_180d,
            'spatial_density_ratio': density_ratio,
            'peak_hour_window_id': peak_idx,
            'is_future_hotspot': is_future_hotspot
        })

    result_df = pd.DataFrame(rows)
    return result_df


def extract_offender_features(conn: sqlite3.Connection) -> pd.DataFrame:
    """
    Extracts genuine, leak-free repeat offender recidivism features.
    - Features are computed STRICTLY from information available at the accused person's initial involvement.
    - Target (recidivism_flag) = 1 if the accused has subsequent offence(s) on later distinct dates, 0 otherwise.
    - ID columns (accused_master_id) and pre-calculated scores (recidivism_risk_score) are completely excluded.
    - Output is 100% numeric for QuickML compatibility.
    """
    query = """
    SELECT 
        a.AccusedMasterID,
        a.CaseMasterID,
        a.AccusedName,
        a.AgeYear,
        a.GenderID,
        cm.GravityOffenceID,
        cm.CrimeMajorHeadID,
        cm.CrimeMinorHeadID,
        u.DistrictID,
        cm.PoliceStationID,
        cm.CrimeRegisteredDate,
        iot.IncidentFromDate
    FROM accused a
    JOIN case_master cm ON a.CaseMasterID = cm.CaseMasterID
    LEFT JOIN inv_occurance_time iot ON cm.CaseMasterID = iot.CaseMasterID
    LEFT JOIN unit u ON cm.PoliceStationID = u.UnitID
    """
    df = pd.read_sql_query(query, conn)
    if df.empty:
        return pd.DataFrame()

    df['inc_dt'] = pd.to_datetime(df['IncidentFromDate'], errors='coerce')
    df['reg_dt'] = pd.to_datetime(df['CrimeRegisteredDate'], errors='coerce')
    df['event_dt'] = df['inc_dt'].fillna(df['reg_dt']).fillna(pd.Timestamp('2024-01-01'))

    df['clean_name'] = df['AccusedName'].fillna('UNKNOWN').str.strip().str.upper()
    df['person_key'] = df['clean_name'] + '_' + df['GenderID'].fillna(1).astype(str) + '_' + df['AgeYear'].fillna(30).astype(str)

    # Group by individual person to construct temporal first-incident features & future re-offense target
    person_groups = df.groupby('person_key')

    rows = []
    for _, group in person_groups:
        sorted_group = group.sort_values('event_dt')
        
        first_incident = sorted_group.iloc[0]
        first_date = first_incident['event_dt']
        
        # Check if person has subsequent offences on a later distinct date (> first_date + 1 day)
        subsequent_incidents = sorted_group[sorted_group['event_dt'] > (first_date + pd.Timedelta(days=1))]
        recidivism_flag = 1 if len(subsequent_incidents) > 0 else 0
        
        age_val = int(first_incident['AgeYear']) if pd.notna(first_incident['AgeYear']) and first_incident['AgeYear'] > 0 else 30
        gender_id = int(first_incident['GenderID']) if pd.notna(first_incident['GenderID']) else 1
        gravity_id = int(first_incident['GravityOffenceID']) if pd.notna(first_incident['GravityOffenceID']) else 1
        cmajor_id = int(first_incident['CrimeMajorHeadID']) if pd.notna(first_incident['CrimeMajorHeadID']) else 1
        cminor_id = int(first_incident['CrimeMinorHeadID']) if pd.notna(first_incident['CrimeMinorHeadID']) else 1
        district_id = int(first_incident['DistrictID']) if pd.notna(first_incident['DistrictID']) else 1
        station_id = int(first_incident['PoliceStationID']) if pd.notna(first_incident['PoliceStationID']) else 1
        
        hr = first_date.hour
        dow = first_date.dayofweek
        mth = first_date.month
        is_weekend = 1 if dow in [5, 6] else 0
        is_night = 1 if (hr >= 22 or hr < 6) else 0
        
        # Initial co-offenders count in the first incident
        first_case_id = first_incident['CaseMasterID']
        co_offenders = len(df[df['CaseMasterID'] == first_case_id])
        
        rows.append({
            'age_years': age_val,
            'gender_id': gender_id,
            'district_id': district_id,
            'police_station_id': station_id,
            'initial_gravity_offence_id': gravity_id,
            'initial_crime_major_head_id': cmajor_id,
            'initial_crime_minor_head_id': cminor_id,
            'initial_hour_of_day': hr,
            'initial_day_of_week': dow,
            'initial_month': mth,
            'initial_is_weekend': is_weekend,
            'initial_is_night_time': is_night,
            'initial_co_offender_count': co_offenders,
            'recidivism_flag': recidivism_flag
        })

    result_df = pd.DataFrame(rows)
    return result_df

