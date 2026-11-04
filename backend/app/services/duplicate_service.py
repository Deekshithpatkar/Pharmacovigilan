from sqlalchemy.orm import Session
from app.api.schemas.case import AdverseEventCaseCreate
from app.models.case import CaseModel

def find_duplicate_case(db: Session, case_data: AdverseEventCaseCreate) -> CaseModel | None:
    """Find an existing case with matching drug, patient details, and similar symptoms."""
    # Search for cases with the same suspected drug (case-insensitive)
    query = db.query(CaseModel).filter(
        CaseModel.suspected_drug.ilike(case_data.suspected_drug.strip())
    )

    # If patient age is provided, match age
    if case_data.patient_age is not None:
        query = query.filter(CaseModel.patient_age == case_data.patient_age)

    # If patient sex is provided, match sex
    if case_data.patient_sex is not None:
        query = query.filter(CaseModel.patient_sex.ilike(case_data.patient_sex.strip()))

    candidates = query.all()

    # Check for keyword overlap in the reaction description
    new_words = set(case_data.reaction_description.lower().split())
    for candidate in candidates:
        existing_words = set(candidate.reaction_description.lower().split())
        shared_words = new_words.intersection(existing_words)
        if len(shared_words) >= 2:
            return candidate

    return None
