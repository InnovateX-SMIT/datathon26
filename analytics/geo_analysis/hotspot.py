from sklearn.cluster import DBSCAN
import pandas as pd
import numpy as np

def find_hotspots_dbscan(coordinates, eps=0.1, min_samples=5):
    """
    DBSCAN Processing, Cluster Extraction, and Cluster Centroids.
    Supports coordinates as:
    - List of dicts: [{'latitude': lat, 'longitude': lon, 'weight': w}, ...] or [{'lat': lat, 'lng': lon}, ...]
    - List of tuples/lists: [(lat, lon), (lat, lon, weight), ...]
    """
    if not coordinates:
        return []
        
    formatted_coords = []
    weights = []
    
    for c in coordinates:
        w = 1.0
        if isinstance(c, dict):
            if 'latitude' in c and 'longitude' in c:
                lat, lon = float(c['latitude']), float(c['longitude'])
                w = float(c.get('weight', c.get('crime_count', 1.0)))
            elif 'lat' in c and 'lng' in c:
                lat, lon = float(c['lat']), float(c['lng'])
                w = float(c.get('weight', c.get('crime_count', 1.0)))
            else:
                continue
        elif isinstance(c, (list, tuple)) and len(c) >= 2:
            lat, lon = float(c[0]), float(c[1])
            if len(c) >= 3:
                w = float(c[2])
        else:
            continue
        formatted_coords.append({'latitude': lat, 'longitude': lon})
        weights.append(w)
        
    if not formatted_coords or sum(weights) < min_samples:
        return []
        
    df = pd.DataFrame(formatted_coords)
    df['weight'] = weights
    X = df[['latitude', 'longitude']].values
    
    try:
        db = DBSCAN(eps=eps, min_samples=min_samples).fit(X, sample_weight=np.array(weights))
        df['cluster'] = db.labels_
    except Exception:
        try:
            db = DBSCAN(eps=eps, min_samples=min_samples).fit(X)
            df['cluster'] = db.labels_
        except Exception:
            return []
    
    # Exclude noise points
    df_clusters = df[df['cluster'] != -1]
    if df_clusters.empty:
        return []
        
    hotspots = []
    grouped = df_clusters.groupby('cluster')
    for cluster_id, group in grouped:
        total_weight = group['weight'].sum()
        if total_weight <= 0:
            continue
        centroid_lat = float((group['latitude'] * group['weight']).sum() / total_weight)
        centroid_lon = float((group['longitude'] * group['weight']).sum() / total_weight)
        crime_count = int(total_weight)
        
        hotspots.append({
            "cluster_id": int(cluster_id),
            "crime_count": crime_count,
            "latitude": centroid_lat,
            "longitude": centroid_lon
        })
        
    hotspots.sort(key=lambda x: x['crime_count'], reverse=True)
    return hotspots
