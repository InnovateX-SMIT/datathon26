import os, sys
sys.path.insert(0, os.path.abspath("."))
import pandas as pd
from backend.core.database import SessionLocal
from backend.services.fir_import_service import FIRImportService

def validate_all_final_datasets():
    dir_path = r"d:\Workplace\Hackathons\Datathon\datathon26\datasets\datasets_final"
    db = SessionLocal()
    fir_importer = FIRImportService(db)
    
    files = [f for f in os.listdir(dir_path) if f.endswith(".csv")]
    results = {}
    
    for f in sorted(files):
        file_path = os.path.join(dir_path, f)
        try:
            df_headers = pd.read_csv(file_path, nrows=0)
            cols = df_headers.columns
            schema_type = fir_importer.detect_schema_type(cols)
            
            # Read first 10 rows to test validation
            df_sample = pd.read_csv(file_path, nrows=10)
            df_sample = df_sample.astype(object).where(pd.notnull(df_sample), None)
            rows = df_sample.to_dict(orient="records")
            
            # Test actual import readiness (schema detection + column mapping + parsing)
            try:
                import_report = fir_importer.import_normalized_dataset(rows, dataset_id=99999, user_id=None, commit=False)
                is_importable = True
                notes = f"ALIGNED & IMPORTABLE (Cols: {len(cols)}, Sample Imported: {import_report.get('cases_inserted')} cases)"
            except Exception as imp_err:
                is_importable = False
                notes = f"Import Error: {imp_err}"
                
            results[f] = {
                "aligned": "YES" if is_importable else "NO",
                "schema_type": schema_type,
                "col_count": len(cols),
                "notes": notes
            }
        except Exception as e:
            results[f] = {
                "aligned": "NO",
                "schema_type": "Error",
                "col_count": 0,
                "notes": str(e)
            }
            
    db.close()
    
    print("\n" + "="*80)
    print(f"{'DATASET FILENAME':<50} | {'ALIGNED':<8} | {'SCHEMA TYPE'}")
    print("="*80)
    for name, info in results.items():
        print(f"{name:<50} | {info['aligned']:<8} | {info['notes']}")
    print("="*80)

if __name__ == "__main__":
    validate_all_final_datasets()
