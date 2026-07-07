import os
import sys
import logging
from sqlalchemy import text

# Ensure project root is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.core.database import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("migration_0002")

def main():
    logger.info("Starting migration 0002 to add dataset column configurations...")
    try:
        with engine.begin() as conn:
            # 1. Update datasets table
            result = conn.execute(text("PRAGMA table_info(datasets)"))
            ds_cols = {row[1] for row in result.fetchall()}
            if ds_cols and "schema_type" not in ds_cols:
                logger.info("Adding schema_type column to datasets table...")
                conn.execute(text("ALTER TABLE datasets ADD COLUMN schema_type VARCHAR(50) DEFAULT 'legacy_crime_intel'"))
            
            # 2. Update case_master table
            result = conn.execute(text("PRAGMA table_info(case_master)"))
            case_cols = {row[1] for row in result.fetchall()}
            if case_cols and "dataset_id" not in case_cols:
                logger.info("Adding dataset_id column to case_master table...")
                conn.execute(text("ALTER TABLE case_master ADD COLUMN dataset_id INTEGER REFERENCES datasets(id) ON DELETE CASCADE"))
                
        logger.info("Migration 0002 completed successfully.")
    except Exception as e:
        logger.error(f"Migration 0002 failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
