import pandas as pd
import random
# pyrefly: ignore [missing-import]
from faker import Faker
from datetime import datetime, timedelta

fake = Faker("en_IN")

# Configuration
NUM_RECORDS = 50000 

crime_types = {
    "Theft": 35,
    "Assault": 20,
    "Fraud": 15,
    "Burglary": 10,
    "Cyber Crime": 8,
    "Drug Offense": 5,
    "Robbery": 4,
    "Kidnapping": 2,
    "Murder": 1
}

districts = [
    "Bengaluru Urban",
    "Bengaluru Rural",
    "Mysuru",
    "Mangaluru",
    "Hubballi",
    "Belagavi",
    "Kalaburagi",
    "Shivamogga",
    "Ballari",
    "Tumakuru"
]

occupations = [
    "Student",
    "Driver",
    "Labourer",
    "Business",
    "Engineer",
    "Teacher",
    "Farmer",
    "Unemployed",
    "Salesman",
    "Government Employee"
]

genders = ["Male", "Female"]

crime_weights = list(crime_types.values())
crime_names = list(crime_types.keys())

records = []

start_date = datetime(2020, 1, 1)

for i in range(NUM_RECORDS):

    crime_type = random.choices(crime_names, weights=crime_weights, k=1)[0]

    district = random.choice(districts)

    crime_date = start_date + timedelta(
        days=random.randint(0, 2000)
    )

    record = {
        "FIR_ID": f"FIR{i+1:07d}",
        "Crime_Type": crime_type,
        "District": district,
        "Police_Station": f"{district[:3].upper()}_PS_{random.randint(1,50)}",
        "Crime_Date": crime_date.strftime("%Y-%m-%d"),
        "Crime_Time": f"{random.randint(0,23):02d}:{random.randint(0,59):02d}",
        "Latitude": round(random.uniform(11.5, 18.5), 6),
        "Longitude": round(random.uniform(74.0, 78.5), 6),
        "Victim_Age": random.randint(18, 70),
        "Accused_Age": random.randint(18, 65),
        "Gender": random.choice(genders),
        "Occupation": random.choice(occupations),
        "Crime_Severity": random.randint(1, 10),
        "Repeat_Offender": random.choices([0, 1], weights=[88, 12])[0],
        "Case_Status": random.choice([
            "Under Investigation",
            "Closed",
            "Chargesheet Filed",
            "Pending Trial"
        ])
    }

    records.append(record)

    if (i + 1) % 100000 == 0:
        print(f"Generated {i+1:,} records")

df = pd.DataFrame(records)

df.to_csv("master_crime_dataset_1M.csv", index=False)

print("\nDataset Created Successfully!")
print(f"Total Records: {len(df):,}")
print("Saved as: master_crime_dataset_1M.csv")