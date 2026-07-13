import os
import sys

# Ensure project root is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.database import SessionLocal, engine
from backend.models import Base, User, UserRole
from database.seed import seed_locations, seed_police_stations
from scripts.seed_fir_lookups import seed_fir_lookups

def seed_users(db):
    if db.query(User).first() is not None:
        print("Users already seeded.")
        return

    users = [
        User(
            id=1,
            name="Administrator",
            email="admin@crimenexus.local",
            password_hash="pbkdf2:sha256:600000$mock_hash",
            role=UserRole.ADMIN,
            status="active"
        ),
        User(
            id=2,
            name="Superintendent Patil",
            email="sp@police.gov.in",
            password_hash="pbkdf2:sha256:600000$mock_hash",
            role=UserRole.SUPERINTENDENT,
            status="active"
        ),
        User(
            id=3,
            name="Officer Sharma",
            email="officer@police.gov.in",
            password_hash="pbkdf2:sha256:600000$mock_hash",
            role=UserRole.OFFICER,
            status="active"
        )
    ]
    db.add_all(users)
    db.commit()
    print("Users Seeded")

def main():
    print("Recreating database tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        seed_users(db)
        seed_fir_lookups(db)
        seed_locations(db)
        seed_police_stations(db)
        print("Completed Successfully")
    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
