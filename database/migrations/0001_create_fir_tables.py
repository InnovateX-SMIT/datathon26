import os
import sys
import logging

# Ensure project root is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.core.database import engine, Base
# Import backend.models to register all models (legacy and new) on the metadata
from backend import models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("migration")

def main():
    logger.info("Initializing creation of new normalized FIR tables...")
    try:
        # create_all is additive: it checks if each table exists, and if not, creates it.
        # It leaves existing tables and data completely untouched.
        Base.metadata.create_all(bind=engine)
        logger.info("Normalized FIR schema database migration completed successfully.")
        logger.info("All new tables are now ensured in the database.")
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
