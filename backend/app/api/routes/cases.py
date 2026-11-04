from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.schemas.case import AdverseEventCaseCreate, AdverseEventCaseResponse, CaseStatus
from app.services import case_service
from app.ai.extraction import extract_case_info
from app.ai.label_retrieval import retrieve_label_evidence

router = APIRouter(prefix="/cases", tags=["Cases"])

@router.post("", response_model=AdverseEventCaseResponse, status_code=status.HTTP_201_CREATED)
def submit_case(case_data: AdverseEventCaseCreate, db: Session = Depends(get_db)):
    """Submit a new adverse event report."""
    case, extracted_info, evidence = case_service.create_case(db, case_data)

    if case.duplicate_of_id:
        message = f"Possible duplicate detected. Linked to {case.duplicate_of_id} for human review."
    else:
        message = "Adverse event report submitted successfully"

    return AdverseEventCaseResponse(
        case_id=case.case_id,
        status=CaseStatus(case.status),
        message=message,
        duplicate_of=case.duplicate_of_id,
        extracted_info=extracted_info,
        evidence=evidence,
    )

@router.get("/{case_id}", response_model=AdverseEventCaseResponse)
def get_case(case_id: str, db: Session = Depends(get_db)):
    """Get status and details of a case by case_id."""
    case = case_service.get_case_by_id(db, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    
    extracted_info = extract_case_info(case.reaction_description, case.suspected_drug)
    search_terms = list(set(extracted_info.reactions + extracted_info.standardized_reactions))
    evidence = retrieve_label_evidence(case.suspected_drug, search_terms)

    return AdverseEventCaseResponse(
        case_id=case.case_id,
        status=CaseStatus(case.status),
        message="Case retrieved successfully",
        duplicate_of=case.duplicate_of_id,
        extracted_info=extracted_info,
        evidence=evidence,
    )
