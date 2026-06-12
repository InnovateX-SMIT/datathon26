from sqlalchemy.orm import Session
from backend.models.report import Report
from typing import List, Optional
from datetime import datetime

class ReportRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_reports(self) -> List[Report]:
        """
        Retrieves all reports sorted by generated_at descending.
        """
        return self.db.query(Report).order_by(Report.generated_at.desc()).all()

    def get_report_by_id(self, report_id: int) -> Optional[Report]:
        """
        Retrieves a report by its ID.
        """
        return self.db.query(Report).filter(Report.id == report_id).first()

    def create_report(self, title: str, report_type: str, summary: Optional[str] = None) -> Report:
        """
        Creates and persists a new report metadata entry.
        """
        db_report = Report(
            title=title,
            report_type=report_type,
            summary=summary,
            generated_at=datetime.utcnow()
        )
        self.db.add(db_report)
        self.db.commit()
        self.db.refresh(db_report)
        return db_report
