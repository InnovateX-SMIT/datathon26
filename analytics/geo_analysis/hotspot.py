from sklearn.cluster import DBSCAN
import pandas as pd
import numpy as np

def find_hotspots_dbscan(coordinates, eps=0.1, min_samples=5):
    """
    DBSCAN Processing, Cluster Extraction, and Cluster Centroids.
    Supports coordinates as:
    - List of dicts: [{'latitude': lat, 'longitude': lon}, ...] or [{'lat': lat, 'lng': lon}, ...]
    - List of tuples/lists: [(lat, lon), ...]
    """
    if not coordinates or len(coordinates) < min_samples:
        return []
        
    formatted_coords = []
    for c in coordinates:
        if isinstance(c, dict):
            if 'latitude' in c and 'longitude' in c:
                formatted_coords.append({'latitude': float(c['latitude']), 'longitude': float(c['longitude'])})
            elif 'lat' in c and 'lng' in c:
                formatted_coords.append({'latitude': float(c['lat']), 'longitude': float(c['lng'])})
        elif isinstance(c, (list, tuple)) and len(c) >= 2:
            formatted_coords.append({'latitude': float(c[0]), 'longitude': float(c[1])})
            
    if not formatted_coords or len(formatted_coords) < min_samples:
        return []
        
    df = pd.DataFrame(formatted_coords)
    X = df[['latitude', 'longitude']].values
    
    db = DBSCAN(eps=eps, min_samples=min_samples).fit(X)
    df['cluster'] = db.labels_
    
    # Exclude noise points
    df_clusters = df[df['cluster'] != -1]
    if df_clusters.empty:
        return []
        
    hotspots = []
    grouped = df_clusters.groupby('cluster')
    for cluster_id, group in grouped:
        centroid_lat = float(group['latitude'].mean())
        centroid_lon = float(group['longitude'].mean())
        crime_count = int(len(group))
        
        hotspots.append({
            "cluster_id": int(cluster_id),
            "crime_count": crime_count,
            "latitude": centroid_lat,
            "longitude": centroid_lon
        })
        
    hotspots.sort(key=lambda x: x['crime_count'], reverse=True)
    return hotspots
