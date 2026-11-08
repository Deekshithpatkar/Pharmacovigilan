from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.schemas.case import CaseStatus
from app.services import review_service

router = APIRouter(prefix="/review", tags=["Review"])

class CaseReviewSummary(BaseModel):
    case_id: str
    reporter_type: str
    suspected_drug: str
    reaction_description: str
    severity: Optional[int]
    status: str
    duplicate_of_id: Optional[str] = None

class HumanReviewSubmitRequest(BaseModel):
    reviewer_notes: str
    adjudicated_status: CaseStatus = CaseStatus.COMPLETED

@router.get("/pending", response_model=List[CaseReviewSummary])
def list_pending_reviews(db: Session = Depends(get_db)):
    """List all cases requiring safety officer / human review."""
    cases = review_service.get_pending_review_cases(db)
    return [
        CaseReviewSummary(
            case_id=c.case_id,
            reporter_type=c.reporter_type,
            suspected_drug=c.suspected_drug,
            reaction_description=c.reaction_description,
            severity=c.severity,
            status=c.status,
            duplicate_of_id=c.duplicate_of_id
        )
        for c in cases
    ]

@router.post("/{case_id}/adjudicate")
def adjudicate_case(
    case_id: str,
    review_req: HumanReviewSubmitRequest,
    db: Session = Depends(get_db)
):
    """Adjudicate and finalize a reviewed case."""
    updated_case = review_service.submit_human_review(
        db,
        case_id=case_id,
        reviewer_notes=review_req.reviewer_notes,
        adjudicated_status=review_req.adjudicated_status
    )
    if not updated_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    return {
        "message": "Case reviewed and updated successfully",
        "case_id": updated_case.case_id,
        "new_status": updated_case.status
    }

