from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.schemas.case import AdverseEventCaseCreate, AdverseEventCaseResponse, CaseStatus
from app.services import case_service
from app.services.audit_service import get_case_audit_trail
from app.ai.extraction import extract_case_info
from app.ai.label_retrieval import retrieve_label_evidence
from app.workflows.react_agent import run_react_agent_investigation

router = APIRouter(prefix="/cases", tags=["Cases"])

@router.post("", response_model=AdverseEventCaseResponse, status_code=status.HTTP_201_CREATED)
def submit_case(case_data: AdverseEventCaseCreate, db: Session = Depends(get_db)):
    """Submit a new adverse event report and run through safety workflow."""
    case, workflow_result = case_service.create_case(db, case_data)

    if case.duplicate_of_id:
        message = f"Possible duplicate detected. Linked to {case.duplicate_of_id} for human review."
    elif workflow_result.route_to_human_reviewer:
        message = f"Case submitted. Routed for human review: {workflow_result.review_reason}"
    else:
        message = "Adverse event report processed and completed successfully."

    return AdverseEventCaseResponse(
        case_id=case.case_id,
        status=CaseStatus(case.status),
        message=message,
        duplicate_of=case.duplicate_of_id,
        extracted_info=workflow_result.extracted_info,
        evidence=workflow_result.evidence,
        triage_priority=workflow_result.triage.priority,
        requires_human_review=workflow_result.route_to_human_reviewer,
        review_reason=workflow_result.review_reason
    )

@router.post("/agent-investigate")
def agent_investigate_case(case_data: AdverseEventCaseCreate, db: Session = Depends(get_db)):
    """Run an autonomous ReAct agent investigation loop, check duplicates, and save to database."""
    return run_react_agent_investigation(db, case_data)

@router.get("/{case_id}/audit")
def get_case_audit(case_id: str, db: Session = Depends(get_db)):
    """Get the complete chronological audit history for a case."""
    logs = get_case_audit_trail(db, case_id)
    return [
        {
            "id": log.id,
            "case_id": log.case_id,
            "action": log.action,
            "previous_status": log.previous_status,
            "new_status": log.new_status,
            "actor": log.actor,
            "details": log.details,
            "timestamp": log.timestamp.isoformat()
        }
        for log in logs
    ]

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
