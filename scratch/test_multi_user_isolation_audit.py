import os
import sys
import unittest
from fastapi.testclient import TestClient

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.main import app
from backend.core.database import get_db, engine, Base

class TestMultiUserIsolation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        cls.client = TestClient(app)

    def test_multi_user_session_data_isolation(self):
        print("\n=======================================================")
        print("  RUNNING MULTI-USER DATA ISOLATION AUDIT & TEST")
        print("=======================================================")
        
        session_a_headers = {
            "X-Session-ID": "session-user-alpha-999"
        }
        session_b_headers = {
            "X-Session-ID": "session-user-beta-888"
        }

        # Legacy compliant headers string
        headers_str = "crime_date,crime_type,district,police_station,latitude,longitude,is_night_time,is_weekend,month,day_of_week,hour_of_day,age_years,co_offender_count,gender_id,risk_tier_id,hotspot_flag_id,recidivism_flag_id,spatial_density_ratio,hist_district_crime_count_30d,hist_station_crime_count_30d\n"

        # 1. USER A uploads Dataset A
        csv_content_a = headers_str + "2026-01-01,Theft,Bengaluru,MG Road PS,12.9716,77.5946,0,0,1,3,14,25,1,1,1,0,0,1.2,15,5\n"
        files_a = {"file": ("user_a_private_data.csv", csv_content_a, "text/csv")}
        data_a = {"display_name": "User A Private Dataset", "description": "Strictly User A data"}

        resp_upload_a = self.client.post(
            "/api/v1/datasets/upload",
            data=data_a,
            files=files_a,
            headers={"X-Session-ID": "session-user-alpha-999"}
        )
        self.assertEqual(resp_upload_a.status_code, 200, f"Upload User A failed: {resp_upload_a.text}")
        ds_a = resp_upload_a.json()
        ds_a_id = ds_a["id"]
        print(f"[TEST PASS 1] User A uploaded Dataset ID {ds_a_id} ('{ds_a['display_name']}')")

        # 2. USER B checks registered datasets
        resp_list_b = self.client.get("/api/v1/datasets/", headers=session_b_headers)
        self.assertEqual(resp_list_b.status_code, 200)
        datasets_b = resp_list_b.json()
        b_ids = [d["id"] for d in datasets_b]
        self.assertNotIn(ds_a_id, b_ids, f"LEAKAGE DETECTED: User A's dataset {ds_a_id} visible to User B!")
        print(f"[TEST PASS 2] User B list datasets check: Dataset {ds_a_id} is NOT visible to User B.")

        # 3. USER B attempts to access User A's dataset ID directly (Cross-User Read/Activate/Delete)
        resp_get_direct = self.client.get(f"/api/v1/datasets/{ds_a_id}", headers=session_b_headers)
        self.assertIn(resp_get_direct.status_code, [404, 403], f"LEAKAGE DETECTED: Direct GET by User B returned {resp_get_direct.status_code}")
        
        resp_act_direct = self.client.post("/api/v1/datasets/activate", json={"dataset_id": ds_a_id}, headers=session_b_headers)
        self.assertIn(resp_act_direct.status_code, [404, 400, 403], f"LEAKAGE DETECTED: Direct Activate by User B returned {resp_act_direct.status_code}")

        resp_del_direct = self.client.delete(f"/api/v1/datasets/{ds_a_id}", headers=session_b_headers)
        self.assertIn(resp_del_direct.status_code, [404, 400, 403], f"LEAKAGE DETECTED: Direct Delete by User B returned {resp_del_direct.status_code}")
        print(f"[TEST PASS 3] Cross-User Unauthorized Access Blocked: User B GET/Activate/Delete on User A dataset failed cleanly.")

        # 4. USER B uploads Dataset B
        csv_content_b = headers_str + "2026-02-01,Robbery,Mysuru,Devaraja PS,12.2958,76.6394,1,1,2,5,22,30,2,1,2,1,1,2.5,20,8\n"
        files_b = {"file": ("user_b_private_data.csv", csv_content_b, "text/csv")}
        data_b = {"display_name": "User B Private Dataset", "description": "Strictly User B data"}

        resp_upload_b = self.client.post(
            "/api/v1/datasets/upload",
            data=data_b,
            files=files_b,
            headers={"X-Session-ID": "session-user-beta-888"}
        )
        self.assertEqual(resp_upload_b.status_code, 200, f"Upload User B failed: {resp_upload_b.text}")
        ds_b = resp_upload_b.json()
        ds_b_id = ds_b["id"]
        print(f"[TEST PASS 4] User B uploaded Dataset ID {ds_b_id} ('{ds_b['display_name']}')")

        # 5. USER A checks datasets — User B's dataset must NOT be visible to User A
        resp_list_a = self.client.get("/api/v1/datasets/", headers=session_a_headers)
        self.assertEqual(resp_list_a.status_code, 200)
        datasets_a = resp_list_a.json()
        a_ids = [d["id"] for d in datasets_a]
        self.assertNotIn(ds_b_id, a_ids, f"LEAKAGE DETECTED: User B's dataset {ds_b_id} visible to User A!")
        print(f"[TEST PASS 5] User A list datasets check: Dataset {ds_b_id} is NOT visible to User A.")

        # Clean up created test datasets
        self.client.delete(f"/api/v1/datasets/{ds_a_id}/permanent", headers=session_a_headers)
        self.client.delete(f"/api/v1/datasets/{ds_b_id}/permanent", headers=session_b_headers)
        print(f"[TEST PASS 6] Cleaned up temporary test datasets.")

if __name__ == "__main__":
    unittest.main()
