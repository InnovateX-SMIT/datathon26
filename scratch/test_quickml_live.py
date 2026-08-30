import os
import sys
sys.path.insert(0, os.path.abspath("."))
from backend.services.prediction_service import PredictionService

def test_quickml():
    print("Testing QuickML Pipelines...")
    svc = PredictionService()
    
    print("\n--- Pipeline 1: Crime Risk ---")
    p1 = svc.predict_crime_risk(
        case_master_id=1,
        district_id=1,
        police_station_id=1,
        crime_major_head_id=2,
        crime_minor_head_id=6,
        gravity_offence_id=2,
        latitude=12.9716,
        longitude=77.5946,
        hour_of_day=22,
        day_of_week=5,
        month=8,
        is_weekend=1,
        is_night_time=1,
        hist_station_crime_count_30d=50,
        hist_district_crime_count_30d=150
    )
    print("P1 Response:", p1)
    
    print("\n--- Pipeline 2: Future Hotspots ---")
    p2 = svc.predict_future_hotspots(
        grid_lat=13.0,
        grid_lon=76.1,
        district_id=9,
        police_station_id=10,
        prior_7d_crime_count=2,
        prior_30d_crime_count=10,
        prior_90d_crime_count=25,
        prior_180d_crime_count=50,
        spatial_density_ratio=0.75,
        peak_hour_window_id=3
    )
    print("P2 Response:", p2)

    print("\n--- Pipeline 3: Recidivism Prediction & XAI ---")
    p3 = svc.predict_recidivism(
        age_years=25,
        gender_id=1,
        district_id=11,
        police_station_id=17,
        initial_gravity_offence_id=2,
        initial_crime_major_head_id=2,
        initial_crime_minor_head_id=12,
        initial_hour_of_day=19,
        initial_day_of_week=6,
        initial_month=12,
        initial_is_weekend=1,
        initial_is_night_time=0,
        initial_co_offender_count=3
    )
    print("P3 Response:", p3)

if __name__ == "__main__":
    test_quickml()
