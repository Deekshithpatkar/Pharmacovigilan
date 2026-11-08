from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.case import CaseModel
from app.api.schemas.case import CaseStatus

def get_pending_review_cases(db: Session) -> List[CaseModel]:
    """Retrieve all cases currently routed for human review."""
    return db.query(CaseModel).filter(
        CaseModel.status == CaseStatus.HUMAN_REVIEW.value
    ).all()

def submit_human_review(
    db: Session,
    case_id: str,
    reviewer_notes: str,
    adjudicated_status: CaseStatus = CaseStatus.COMPLETED
) -> Optional[CaseModel]:
    """Allow a safety reviewer to inspect, add notes, and finalize a case."""
    case = db.query(CaseModel).filter(CaseModel.case_id == case_id).first()
    if not case:
        return None

    # Append reviewer notes to case record
    existing_notes = case.additional_information or ""
    separator = "\n---\n" if existing_notes else ""
    case.additional_information = f"{existing_notes}{separator}Reviewer Note: {reviewer_notes}"
    case.status = adjudicated_status.value

    db.commit()
    db.refresh(case)
    return case

