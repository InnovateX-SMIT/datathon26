import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from backend.services.fir_synthetic_generator import FIRSyntheticDataGenerator

def test_synthetic_fir_dataset_coordinates_in_karnataka():
    # 1. Load the generated dataset
    csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "synthetic_fir_dataset.csv")
    assert os.path.exists(csv_path), "synthetic_fir_dataset.csv does not exist"

    df = pd.read_csv(csv_path)
    assert len(df) > 0, "synthetic_fir_dataset.csv is empty"

    # 2. Load Karnataka state boundary dissolved geometry
    geojson_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "karnataka_boundary.geojson")
    assert os.path.exists(geojson_path), "karnataka_boundary.geojson does not exist"

    gdf = gpd.read_file(geojson_path)
    karnataka_geom = gdf.geometry.iloc[0]

    # 3. Check every coordinate in the CSV is inside Karnataka
    outside_count = 0
    outside_list = []
    for idx, row in df.iterrows():
        lat = row['latitude']
        lon = row['longitude']
        p = Point(lon, lat)
        if not karnataka_geom.contains(p):
            outside_count += 1
            outside_list.append((lat, lon))

    assert outside_count == 0, f"Found {outside_count} coordinates outside Karnataka boundary. Examples: {outside_list[:5]}"

def test_generator_output_reproducible_and_constrained():
    # Verify generator runs and enforces Karnataka constraints
    generator = FIRSyntheticDataGenerator()
    assert generator.karnataka_geom is not None, "Karnataka boundary geom should be loaded in generator"

    records = generator.generate(num_records=10)
    assert len(records) > 0

    from shapely.geometry import Point
    for row in records:
        lat = row['latitude']
        lon = row['longitude']
        p = Point(lon, lat)
        assert generator.karnataka_geom.contains(p), f"Generated coordinate ({lat}, {lon}) is outside Karnataka boundary"
