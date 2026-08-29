from sklearn.cluster import DBSCAN
import pandas as pd
import numpy as np

def find_hotspots_dbscan(coordinates, eps=0.1, min_samples=5):
    """
    DBSCAN Processing, Cluster Extraction, and Cluster Centroids.
    Supports coordinates as:
    - List of dicts: [{'latitude': lat, 'longitude': lon, 'weight': w, 'date': ...}, ...]
    - List of tuples/lists: [(lat, lon), (lat, lon, weight), (lat, lon, weight, date), ...]
    Provides descriptive historical spatiotemporal clustering.
    """
    if not coordinates:
        return []
        
    formatted_coords = []
    weights = []
    dates = []
    hours = []
    
    for c in coordinates:
        w = 1.0
        d_val = None
        h_val = None
        if isinstance(c, dict):
            if 'latitude' in c and 'longitude' in c:
                lat, lon = float(c['latitude']), float(c['longitude'])
                w = float(c.get('weight', c.get('crime_count', 1.0)))
                d_val = c.get('date', c.get('incident_date', c.get('crime_date')))
                h_val = c.get('hour')
            elif 'lat' in c and 'lng' in c:
                lat, lon = float(c['lat']), float(c['lng'])
                w = float(c.get('weight', c.get('crime_count', 1.0)))
                d_val = c.get('date', c.get('incident_date', c.get('crime_date')))
                h_val = c.get('hour')
            else:
                continue
        elif isinstance(c, (list, tuple)) and len(c) >= 2:
            lat, lon = float(c[0]), float(c[1])
            if len(c) >= 3:
                w = float(c[2])
            if len(c) >= 4:
                d_val = c[3]
            if len(c) >= 5:
                h_val = c[4]
        else:
            continue
        formatted_coords.append({'latitude': lat, 'longitude': lon})
        weights.append(w)
        dates.append(str(d_val) if d_val is not None else None)
        hours.append(int(h_val) if h_val is not None else None)
        
    if not formatted_coords or sum(weights) < min_samples:
        return []
        
    df = pd.DataFrame(formatted_coords)
    df['weight'] = weights
    df['date'] = dates
    df['hour'] = hours
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
        
        valid_dates = [d for d in group['date'].dropna() if d]
        first_date = min(valid_dates) if valid_dates else None
        last_date = max(valid_dates) if valid_dates else None
        
        valid_hours = [h for h in group['hour'].dropna() if h is not None]
        if valid_hours:
            peak_h = max(set(valid_hours), key=valid_hours.count)
            peak_hour_window = f"{peak_h:02d}:00 - {(peak_h + 2) % 24:02d}:00"
        else:
            peak_hour_window = "18:00 - 22:00 (Standard Evening Peak)"
        
        temporal_cat = "Recurring Historical Cluster"
        if first_date and last_date and first_date != last_date:
            try:
                from datetime import date
                d1 = date.fromisoformat(first_date[:10])
                d2 = date.fromisoformat(last_date[:10])
                days_span = (d2 - d1).days
                if days_span <= 14:
                    temporal_cat = "Concentrated Historical Surge"
                elif days_span > 60:
                    temporal_cat = "Persistent Historical Hotspot"
            except Exception:
                pass
        
        hotspots.append({
            "cluster_id": int(cluster_id),
            "crime_count": crime_count,
            "latitude": centroid_lat,
            "longitude": centroid_lon,
            "first_incident_date": first_date,
            "last_incident_date": last_date,
            "peak_hour_window": peak_hour_window,
            "temporal_category": temporal_cat,
            "hotspot_type": "Historical Descriptive Cluster"
        })
        
    hotspots.sort(key=lambda x: x['crime_count'], reverse=True)
    return hotspots

