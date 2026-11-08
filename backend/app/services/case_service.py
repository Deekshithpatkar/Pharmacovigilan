import uuid
from typing import Tuple
from sqlalchemy.orm import Session
from app.api.schemas.case import AdverseEventCaseCreate, CaseStatus
from app.models.case import CaseModel
from app.services.duplicate_service import find_duplicate_case
from app.ai.extraction import extract_case_info
from app.ai.label_retrieval import retrieve_label_evidence
from app.workflows.case_workflow import run_case_workflow, CaseWorkflowResult
from app.services.audit_service import record_audit_log

def generate_case_id() -> str:
    """Generate a unique human-readable case ID, e.g. PV-8F3A2B1C."""
    return f"PV-{uuid.uuid4().hex[:8].upper()}"

def create_case(db: Session, case_data: AdverseEventCaseCreate) -> Tuple[CaseModel, CaseWorkflowResult]:
    """
    Process an adverse event report end-to-end:
    1. Check for duplicates.
    2. Extract information using AI.
    3. Retrieve drug-label evidence.
    4. Execute workflow orchestration & safety triage.
    5. Save case record to database with final status.
    """
    # 1. Duplicate check
    duplicate = find_duplicate_case(db, case_data)
    is_duplicate = duplicate is not None
    duplicate_of_id = duplicate.case_id if duplicate else None

    # 2. AI Information Extraction
    extracted_info = extract_case_info(case_data.reaction_description, case_data.suspected_drug)

    # 3. Drug-Label Evidence Retrieval (RAG)
    search_terms = list(set(extracted_info.reactions + extracted_info.standardized_reactions))
    evidence = retrieve_label_evidence(case_data.suspected_drug, search_terms)

    # 4. Workflow Orchestration & Human Review Routing
    workflow_result = run_case_workflow(
        case_data=case_data,
        is_duplicate=is_duplicate,
        extracted_info=extracted_info,
        evidence=evidence
    )

    # 5. Persist to database
    db_case = CaseModel(
        case_id=generate_case_id(),
        reporter_type=case_data.reporter_type.value,
        patient_age=case_data.patient_age,
        patient_sex=case_data.patient_sex,
        suspected_drug=case_data.suspected_drug,
        reaction_description=case_data.reaction_description,
        drug_start_date=case_data.drug_start_date,
        reaction_start_date=case_data.reaction_start_date,
        outcome=case_data.outcome or extracted_info.outcome,
        additional_information=case_data.additional_information,
        status=workflow_result.final_status.value,
        severity=extracted_info.severity,
        duplicate_of_id=duplicate_of_id,
    )
    db.add(db_case)
    db.commit()
    db.refresh(db_case)

    # 6. Record initial audit log entry
    record_audit_log(
        db=db,
        case_id=db_case.case_id,
        action="CASE_CREATED",
        new_status=db_case.status,
        actor=case_data.reporter_type.value,
        details=f"Case created with triage priority {workflow_result.triage.priority}. Reason: {workflow_result.review_reason}"
    )

    return db_case, workflow_result

def get_case_by_id(db: Session, case_id: str) -> CaseModel | None:
    """Retrieve a case from the database by its case_id."""
    return db.query(CaseModel).filter(CaseModel.case_id == case_id).first()
