import os
import sys
sys.path.insert(0, os.path.abspath("."))
import unittest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.core.database import SessionLocal
from backend.models.dataset import Dataset

class TestDeletionPersistence(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.headers_user_a = {"X-Session-ID": "deletion-test-session-alpha-123"}
        self.headers_user_b = {"X-Session-ID": "deletion-test-session-beta-456"}

    def test_complete_deletion_lifecycle(self):
        print("\n" + "="*70)
        print("  RUNNING DELETION PERSISTENCE & NO-REAPPEARANCE AUDIT")
        print("="*70)

        # 1. Ensure clean slate for User A
        res_list = self.client.get("/api/v1/datasets/", headers=self.headers_user_a)
        self.assertEqual(res_list.status_code, 200)
        for ds in res_list.json():
            self.client.delete(f"/api/v1/datasets/{ds['id']}/permanent", headers=self.headers_user_a)

        # Confirm 0 datasets for User A
        res_list_empty = self.client.get("/api/v1/datasets/", headers=self.headers_user_a)
        self.assertEqual(len(res_list_empty.json()), 0)
        print("[TEST PASS 1] Starting state clean: 0 active/registered datasets.")

        # 2. Upload Dataset A
        csv_content = b"crime_no,registered_date,unit,act_code,section_code,district,state,case_category,gravity_offence\n100010001202500001,2025-01-15,Bengaluru City PS,IPC,302,Bengaluru Urban,Karnataka,Grave,Grave\n"
        files = {"file": ("test_persist_a.csv", csv_content, "text/csv")}
        res_upload = self.client.post("/api/v1/datasets/upload", files=files, headers=self.headers_user_a)
        self.assertEqual(res_upload.status_code, 200)
        dataset_a_id = res_upload.json()["id"]
        print(f"[TEST PASS 2] Dataset A uploaded (ID {dataset_a_id}).")

        # 3. Permanently Delete Dataset A
        res_del = self.client.delete(f"/api/v1/datasets/{dataset_a_id}/permanent", headers=self.headers_user_a)
        self.assertEqual(res_del.status_code, 200)
        print(f"[TEST PASS 3] Dataset A (ID {dataset_a_id}) permanently deleted.")

        # 4. Verify Dataset Manager shows 0 datasets
        res_list_after_del = self.client.get("/api/v1/datasets/", headers=self.headers_user_a)
        self.assertEqual(len(res_list_after_del.json()), 0)
        print("[TEST PASS 4] Dataset Manager list is empty (0 datasets).")

        # 5. Verify querying deleted dataset directly returns 404
        res_get_deleted = self.client.get(f"/api/v1/datasets/{dataset_a_id}", headers=self.headers_user_a)
        self.assertEqual(res_get_deleted.status_code, 404)
        print(f"[TEST PASS 5] Direct access to deleted Dataset ID {dataset_a_id} returns 404 Not Found.")

        # 6. Verify analytics API call when empty does NOT recreate dataset
        res_analytics = self.client.get("/api/v1/analytics/summary", headers=self.headers_user_a)
        # Should either return empty dashboard payload or 200 with 0 count
        self.assertIn(res_analytics.status_code, [200, 404])
        
        # Verify Dataset Manager is STILL 0 datasets (No silent auto-creation!)
        res_list_after_analytics = self.client.get("/api/v1/datasets/", headers=self.headers_user_a)
        self.assertEqual(len(res_list_after_analytics.json()), 0)
        print("[TEST PASS 6] API navigation did NOT auto-recreate or restore deleted datasets.")

        # 7. Restart Backend Simulation (create new DB session & service instances)
        db_new = SessionLocal()
        from backend.core.dataset_resolver import DatasetResolver
        from backend.core.exceptions import NoActiveDatasetException
        resolver = DatasetResolver(db_new, session_id="deletion-test-session-alpha-123")
        with self.assertRaises(NoActiveDatasetException):
            resolver.get_active_dataset_id()
        db_new.close()
        print("[TEST PASS 7] Service re-initialization raises NoActiveDatasetException — Zero auto-restoration!")

        print("="*70)
        print("  ALL DELETION PERSISTENCE TESTS PASSED SUCCESSFULLY!")
        print("="*70)

if __name__ == "__main__":
    unittest.main()
