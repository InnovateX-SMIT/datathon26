import os
import sys

# Ensure backend package can be imported from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.fir_synthetic_generator import FIRSyntheticDataGenerator
import pandas as pd
import numpy as np

def main():
    print("Generating synthetic datasets...")
    
    # 1. Generate FIR Normalized dataset
    generator = FIRSyntheticDataGenerator()
    csv_path = "datasets/processed/fir_normalized_seed.csv"
    excel_path = "datasets/processed/fir_normalized_seed.xlsx"
    
    os.makedirs("datasets/processed", exist_ok=True)
    generator.generate_and_export(csv_path, excel_path, num_records=50)
    print(f"Generated FIR dataset with 50 cases: {csv_path} & {excel_path}")
    
    # 2. Generate Legacy Crime Events dataset
    # We will generate a basic legacy crimes CSV to test the legacy upload path
    legacy_data = []
    crime_types = ["Theft", "Assault", "Murder", "Narcotics", "Public Nuisance"]
    districts = ["Mysuru", "Ballari", "Bengaluru City", "Dharwad", "Belagavi"]
    stations = ["Devaraja PS", "Gandhinagar PS", "Town PS", "Cantonment PS", "Rural PS"]
    genders = ["Male", "Female", "Transgender"]
    occupations = ["Farmer", "Business", "Labourer", "Driver", "Techie", "Unemployed"]
    statuses = ["reported", "investigating", "chargesheeted", "closed"]
    
    np.random.seed(42)
    for i in range(100):
        legacy_data.append({
            "fir_id": f"L_FIR{i:03d}",
            "crime_type": np.random.choice(crime_types),
            "crime_date": (pd.Timestamp("2025-01-01") + pd.to_timedelta(np.random.randint(0, 365), unit="D")).strftime("%Y-%m-%d"),
            "crime_time": f"{np.random.randint(0, 24):02d}:{np.random.randint(0, 60):02d}",
            "district": np.random.choice(districts),
            "police_station": np.random.choice(stations),
            "victim_age": int(np.random.randint(5, 80)),
            "accused_age": int(np.random.randint(18, 70)),
            "gender": np.random.choice(genders),
            "occupation": np.random.choice(occupations),
            "repeat_offender": int(np.random.choice([0, 1])),
            "severity": float(np.random.uniform(1.0, 5.0)),
            "status": np.random.choice(statuses)
        })
        
    df_legacy = pd.DataFrame(legacy_data)
    df_legacy.to_csv("datasets/processed/legacy_seed.csv", index=False)
    df_legacy.to_excel("datasets/processed/legacy_seed.xlsx", index=False, engine="openpyxl")
    print("Generated Legacy dataset with 100 crimes: datasets/processed/legacy_seed.csv & .xlsx")

if __name__ == "__main__":
    main()
