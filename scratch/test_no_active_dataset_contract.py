import os
import sys
sys.path.insert(0, os.path.abspath("."))
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from backend.app.main import app

class TestNoActiveDatasetContract(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.headers = {"X-Session-ID": "test-empty-contract-session-999"}
        
        # Ensure clean slate: delete all active datasets for this session
        res_list = self.client.get("/api/v1/datasets/", headers=self.headers)
        if res_list.status_code == 200:
            for ds in res_list.json():
                self.client.delete(f"/api/v1/datasets/{ds['id']}/permanent", headers=self.headers)

    def test_recommendations_list_returns_empty(self):
        # Problem 2 Fix Verification: GET /recommendations/ returns [] when 0 active datasets exist
        res = self.client.get("/api/v1/recommendations/", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), [])
        print("[TEST PASS - RECOMMENDATIONS] GET /recommendations/ returns [] (0 stale historical recs).")

    def test_recommendations_solve_returns_404(self):
        # Problem 1 Fix Verification: POST /recommendations/solve returns 400/404 controlled error (NOT 500!)
        payload = {
            "district": "Bengaluru Urban",
            "sanctioned_asi": 10,
            "sanctioned_chc": 20,
            "sanctioned_cpc": 50
        }
        res = self.client.post("/api/v1/recommendations/solve", json=payload, headers=self.headers)
        print("SOLVE RESPONSE:", res.status_code, res.json())
        self.assertIn(res.status_code, [404, 400])
        msg = res.json().get("message") or res.json().get("detail", "")
        self.assertIn("No active dataset selected", msg)
        print("[TEST PASS - SOLVER CONTRACT] POST /recommendations/solve returns clean controlled error.")

    @patch("backend.services.prediction_service.requests.post")
    def test_quickml_pipeline3_guarded_when_no_active_dataset(self, mock_post):
        # Problem 3 Fix Verification: QuickML is NEVER called when 0 active datasets exist
        res = self.client.get("/api/v1/predictions/recidivism?age_years=25", headers=self.headers)
        print("RECIDIVISM RESPONSE:", res.status_code, res.json())
        self.assertIn(res.status_code, [404, 400])
        msg = res.json().get("message") or res.json().get("detail", "")
        self.assertIn("No active dataset selected", msg)
        mock_post.assert_not_called()
        print("[TEST PASS - QUICKML GUARD] Pipeline 3 prediction blocked, QuickML call count == 0.")

if __name__ == "__main__":
    unittest.main()
