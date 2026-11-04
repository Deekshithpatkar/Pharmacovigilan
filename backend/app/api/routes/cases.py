from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.schemas.case import AdverseEventCaseCreate, AdverseEventCaseResponse, CaseStatus
from app.services import case_service

router = APIRouter(prefix="/cases", tags=["Cases"])

@router.post("", response_model=AdverseEventCaseResponse, status_code=status.HTTP_201_CREATED)
def submit_case(case_data: AdverseEventCaseCreate, db: Session = Depends(get_db)):
    """Submit a new adverse event report."""
    case = case_service.create_case(db, case_data)
    return AdverseEventCaseResponse(
        case_id=case.case_id,
        status=CaseStatus(case.status),
        message="Adverse event report submitted successfully",
    )

@router.get("/{case_id}", response_model=AdverseEventCaseResponse)
def get_case(case_id: str, db: Session = Depends(get_db)):
    """Get status and details of a case by case_id."""
    case = case_service.get_case_by_id(db, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    return AdverseEventCaseResponse(
        case_id=case.case_id,
        status=CaseStatus(case.status),
        message="Case retrieved successfully",
    )
