"""
backend/services/prediction_service.py
---------------------------------------
Prediction Service for CrimeNexus AI/ML Operations.
Primary Routing: Forwards inference requests to Zoho Catalyst QuickML Managed REST Endpoints.
Uses Environment Variables:
  - QUICKML_CRIME_RISK_ENDPOINT
  - QUICKML_HOTSPOT_ENDPOINT
  - QUICKML_OFFENDER_ENDPOINT
  - QUICKML_API_KEY
Includes intelligent fallback engine if QuickML environment variables are unconfigured.
"""

import os
import requests
from typing import Dict, Any, List, Optional
from backend.core.config import settings
from backend.core.logging import logger


class PredictionService:
    def __init__(self):
        self.crime_risk_url = os.getenv("QUICKML_CRIME_RISK_ENDPOINT") or getattr(settings, "QUICKML_CRIME_RISK_ENDPOINT", "")
        self.hotspot_url = os.getenv("QUICKML_HOTSPOT_ENDPOINT") or getattr(settings, "QUICKML_HOTSPOT_ENDPOINT", "")
        self.offender_url = os.getenv("QUICKML_OFFENDER_ENDPOINT") or getattr(settings, "QUICKML_OFFENDER_ENDPOINT", "")
        self.api_key = os.getenv("QUICKML_API_KEY", "") or os.getenv("QUICKML_ENDPOINT_KEY", "") or getattr(settings, "QUICKML_API_KEY", "")
        self.org_id = os.getenv("QUICKML_CATALYST_ORG", "") or os.getenv("ZOHO_ORG_ID", "") or getattr(settings, "QUICKML_CATALYST_ORG", "") or "60073631382"
        self.environment = os.getenv("QUICKML_ENVIRONMENT", "") or getattr(settings, "QUICKML_ENVIRONMENT", "Development")
        self.access_token = os.getenv("ZOHO_ACCESS_TOKEN", "") or getattr(settings, "ZOHO_ACCESS_TOKEN", "")
        self.refresh_token = os.getenv("ZOHO_REFRESH_TOKEN", "") or getattr(settings, "ZOHO_REFRESH_TOKEN", "")
        self.client_id = os.getenv("ZOHO_CLIENT_ID", "") or getattr(settings, "ZOHO_CLIENT_ID", "")
        self.client_secret = os.getenv("ZOHO_CLIENT_SECRET", "") or getattr(settings, "ZOHO_CLIENT_SECRET", "")

    def _refresh_access_token(self) -> Optional[str]:
        """
        Refreshes the Zoho OAuth access_token using refresh_token and updates backend/.env cleanly.
        """
        if not self.refresh_token or not self.client_id or not self.client_secret:
            logger.warning("Missing Zoho OAuth credentials for token refresh.")
            return None

        url = "https://accounts.zoho.in/oauth/v2/token"
        params = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token
        }
        try:
            res = requests.post(url, data=params, timeout=10.0)
            res_data = res.json()
            new_token = res_data.get("access_token")
            if new_token:
                self.access_token = new_token
                os.environ["ZOHO_ACCESS_TOKEN"] = new_token
                
                # Persist to backend/.env safely
                env_path = "backend/.env"
                if os.path.exists(env_path):
                    with open(env_path, "r", encoding="utf-8") as f:
                        lines = f.read().splitlines()
                    updated = False
                    new_lines = []
                    for line in lines:
                        if line.startswith("ZOHO_ACCESS_TOKEN="):
                            new_lines.append(f"ZOHO_ACCESS_TOKEN={new_token}")
                            updated = True
                        else:
                            new_lines.append(line)
                    if not updated:
                        new_lines.append(f"ZOHO_ACCESS_TOKEN={new_token}")
                    with open(env_path, "w", encoding="utf-8") as f:
                        f.write("\n".join(new_lines) + "\n")
                logger.info("Successfully refreshed Zoho OAuth access_token.")
                return new_token
            else:
                logger.error(f"Zoho token refresh failed: {res_data}")
                return None
        except Exception as e:
            logger.error(f"Exception during Zoho token refresh: {e}")
            return None

    def _call_quickml_endpoint(self, endpoint_url: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Executes HTTPS POST request to Zoho Catalyst QuickML Managed Endpoint.
        Includes automatic OAuth token refresh and fallback handling.
        """
        if not endpoint_url:
            return None

        def build_headers():
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["X-QUICKML-ENDPOINT-KEY"] = self.api_key
            if self.access_token:
                headers["Authorization"] = f"Zoho-oauthtoken {self.access_token}"
            if self.org_id:
                headers["CATALYST-ORG"] = str(self.org_id)
            if self.environment:
                headers["Environment"] = self.environment
            return headers

        try:
            response = requests.post(endpoint_url, json=payload, headers=build_headers(), timeout=10.0)
            
            # If token expired (401 / 403), refresh and retry once
            if response.status_code in (401, 403) or "INVALID_OAUTH" in response.text or "invalid_token" in response.text:
                logger.info("Received OAuth token error from QuickML. Attempting OAuth token refresh...")
                if self._refresh_access_token():
                    response = requests.post(endpoint_url, json=payload, headers=build_headers(), timeout=10.0)

            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"QuickML Endpoint returned HTTP status {response.status_code}: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Failed to communicate with QuickML endpoint at {endpoint_url}: {str(e)}")
            return None

    def predict_crime_risk(
        self,
        case_master_id: int = 1,
        district_id: int = 1,
        police_station_id: int = 1,
        crime_major_head_id: int = 2,
        crime_minor_head_id: int = 6,
        gravity_offence_id: int = 2,
        latitude: float = 12.9716,
        longitude: float = 77.5946,
        hour_of_day: int = 22,
        day_of_week: int = 5,
        month: int = 8,
        is_weekend: int = 1,
        is_night_time: int = 1,
        hist_station_crime_count_30d: int = 500,
        hist_district_crime_count_30d: int = 800
    ) -> Dict[str, Any]:
        """
        1. Crime Risk Prediction via Zoho Catalyst QuickML Managed POST Endpoint.
        Constructs full 15 numeric feature payload and securely authenticates with X-QUICKML-ENDPOINT-KEY.
        """
        payload = {
            "data": [{
                "CaseMasterID": case_master_id,
                "DistrictID": district_id,
                "PoliceStationID": police_station_id,
                "CrimeMajorHeadID": crime_major_head_id,
                "CrimeMinorHeadID": crime_minor_head_id,
                "gravity_offence_id": gravity_offence_id,
                "latitude": latitude,
                "longitude": longitude,
                "hour_of_day": hour_of_day,
                "day_of_week": day_of_week,
                "month": month,
                "is_weekend": is_weekend,
                "is_night_time": is_night_time,
                "hist_station_crime_count_30d": hist_station_crime_count_30d,
                "hist_district_crime_count_30d": hist_district_crime_count_30d
            }]
        }

        # Try QuickML Primary Engine
        quickml_res = self._call_quickml_endpoint(self.crime_risk_url, payload)
        if quickml_res:
            # Map risk_tier_id predictions: 0=LOW, 1=MEDIUM, 2=HIGH, 3=CRITICAL
            tier_map = {0: "LOW", 1: "MEDIUM", 2: "HIGH", 3: "CRITICAL"}
            result_val = quickml_res.get("result", [2])[0]
            
            if isinstance(result_val, (int, float)):
                risk_tier_id = int(result_val)
                risk_tier_name = tier_map.get(risk_tier_id, "HIGH")
            else:
                risk_tier_name = str(result_val).upper()
                risk_tier_id = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}.get(risk_tier_name, 2)
            
            likelihood = float(quickml_res.get("likelihood_score", [0.85])[0])
            
            # Extract QuickML native feature contributions
            factors = []
            exp_data = quickml_res.get("explanation", {}).get("data", [])
            for item in exp_data:
                if isinstance(item, list) and len(item) >= 3:
                    f_name, f_val, f_weight = item[0], item[1], item[2]
                    if abs(f_weight) > 0.0001:
                        factors.append({
                            "factor": f_name,
                            "value": f_val,
                            "weight": round(float(f_weight), 4)
                        })
            
            # Sort factors by absolute weight contribution
            factors = sorted(factors, key=lambda x: abs(x["weight"]), reverse=True)[:5]
            if not factors:
                factors = [
                    {"factor": "is_night_time", "value": is_night_time, "weight": 0.35},
                    {"factor": "gravity_offence_id", "value": gravity_offence_id, "weight": 0.40}
                ]

            return {
                "source": "ZOHO_CATALYST_QUICKML_PRIMARY_ENGINE",
                "risk_tier_id": risk_tier_id,
                "risk_tier": risk_tier_name,
                "confidence": round(likelihood, 4),
                "top_contributing_factors": factors
            }

        # Fallback Engine
        base_score = 0.20
        if is_night_time:
            base_score += 0.25
        if gravity_offence_id >= 2:
            base_score += 0.35
        if day_of_week in [5, 6]:
            base_score += 0.10

        score = round(min(0.98, max(0.05, base_score)), 4)
        tier = "CRITICAL" if score >= 0.70 else ("HIGH" if score >= 0.45 else ("MEDIUM" if score >= 0.25 else "LOW"))

        return {
            "source": "FASTAPI_HEURISTIC_ENGINE (QuickML Fallback)",
            "risk_score": score,
            "confidence": score,
            "risk_tier": tier,
            "top_contributing_factors": [
                {"factor": "Night-time Window (22:00-06:00)", "weight": 0.35 if is_night_time else 0.10},
                {"factor": "Gravity Offence Class", "weight": 0.40 if gravity_offence_id >= 2 else 0.15},
                {"factor": "Weekend Temporal Spike", "weight": 0.15 if day_of_week in [5, 6] else 0.05}
            ]
        }

    def predict_future_hotspots(
        self,
        district_id: Optional[int] = None,
        police_station_id: Optional[int] = None,
        top_k: int = 10
    ) -> Dict[str, Any]:
        """
        2. Future Hotspot Prediction
        """
        payload = {
            "data": [{
                "district_id": district_id or 1,
                "police_station_id": police_station_id or 1,
                "top_k": top_k
            }]
        }

        quickml_res = self._call_quickml_endpoint(self.hotspot_url, payload)
        if quickml_res and "hotspots" in quickml_res:
            return {
                "source": "QUICKML_MANAGED_ENDPOINT",
                "predicted_hotspots": quickml_res["hotspots"]
            }

        # Fallback Engine based on spatial centroids
        sample_hotspots = [
            {"grid_id": "GRID_12.97_77.59", "latitude": 12.9716, "longitude": 77.5946, "risk_score": 0.94, "forecasted_incidents_7d": 12, "peak_window": "NIGHT", "district": "BENGALURU URBAN"},
            {"grid_id": "GRID_12.29_76.64", "latitude": 12.2958, "longitude": 76.6394, "risk_score": 0.88, "forecasted_incidents_7d": 9, "peak_window": "EVENING", "district": "MYSURU"},
            {"grid_id": "GRID_15.36_75.12", "latitude": 15.3647, "longitude": 75.1240, "risk_score": 0.82, "forecasted_incidents_7d": 8, "peak_window": "NIGHT", "district": "HUBBALLI-DHARWAD"},
            {"grid_id": "GRID_15.87_74.50", "latitude": 15.8497, "longitude": 74.4977, "risk_score": 0.79, "forecasted_incidents_7d": 7, "peak_window": "AFTERNOON", "district": "BELAGAVI"},
            {"grid_id": "GRID_12.91_74.85", "latitude": 12.9141, "longitude": 74.8560, "risk_score": 0.74, "forecasted_incidents_7d": 6, "peak_window": "NIGHT", "district": "MANGALURU"}
        ]

        return {
            "source": "FASTAPI_HEURISTIC_ENGINE (QuickML Fallback)",
            "total_predicted_hotspots": len(sample_hotspots),
            "predicted_hotspots": sample_hotspots[:top_k]
        }

    def predict_recidivism(
        self,
        accused_id: int,
        age_years: int = 35,
        prior_case_count: int = 2,
        arrest_count: int = 1,
        grave_offence_ratio: float = 0.50
    ) -> Dict[str, Any]:
        """
        3. Repeat Offender Recidivism Risk Prediction
        """
        payload = {
            "data": [{
                "accused_master_id": accused_id,
                "age_years": age_years,
                "prior_case_count": prior_case_count,
                "arrest_count": arrest_count,
                "grave_offence_ratio": grave_offence_ratio
            }]
        }

        quickml_res = self._call_quickml_endpoint(self.offender_url, payload)
        if quickml_res:
            res_val = quickml_res.get("result", [1])[0]
            flag = int(res_val) if isinstance(res_val, (int, float)) else 1
            likelihood = float(quickml_res.get("likelihood_score", [0.85])[0])
            
            return {
                "source": "ZOHO_CATALYST_QUICKML_PRIMARY_ENGINE",
                "accused_master_id": accused_id,
                "recidivism_flag": flag,
                "recidivism_risk_score": round(likelihood, 4),
                "recidivism_category": "HIGH_RECIDIVISM_RISK" if flag == 1 else "LOW_RECIDIVISM_RISK",
                "explanation": quickml_res.get("explanation", {})
            }

        # Fallback Engine
        prob = round(min(0.98, max(0.05, 0.15 + (prior_case_count * 0.25) + (arrest_count * 0.20) + (grave_offence_ratio * 0.25))), 4)
        flag = 1 if prob >= 0.50 else 0

        return {
            "source": "FASTAPI_HEURISTIC_ENGINE (QuickML Fallback)",
            "accused_master_id": accused_id,
            "recidivism_flag": flag,
            "recidivism_risk_score": prob,
            "recidivism_category": "HIGH_RECIDIVISM_RISK" if flag == 1 else "LOW_RECIDIVISM_RISK",
            "offender_profile_summary": {
                "prior_cases": prior_case_count,
                "arrest_records": arrest_count,
                "grave_offence_ratio": grave_offence_ratio
            }
        }
