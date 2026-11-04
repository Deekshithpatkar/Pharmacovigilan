from sqlalchemy.orm import Session
from app.api.schemas.case import AdverseEventCaseCreate
from app.models.case import CaseModel
from app.ai.normalization import normalize_drug_name

def find_duplicate_case(db: Session, case_data: AdverseEventCaseCreate) -> CaseModel | None:
    """Find an existing case with matching normalized drug, patient details, and similar symptoms."""
    normalized_new_drug = normalize_drug_name(case_data.suspected_drug)

    query = db.query(CaseModel)

    # Match patient age if provided
    if case_data.patient_age is not None:
        query = query.filter(CaseModel.patient_age == case_data.patient_age)

    # Match patient sex if provided
    if case_data.patient_sex is not None:
        query = query.filter(CaseModel.patient_sex.ilike(case_data.patient_sex.strip()))

    candidates = query.all()

    # Check for matching normalized drug and symptom keyword overlap
    new_words = set(case_data.reaction_description.lower().split())
    for candidate in candidates:
        candidate_drug = normalize_drug_name(candidate.suspected_drug)
        if candidate_drug.lower() == normalized_new_drug.lower():
            existing_words = set(candidate.reaction_description.lower().split())
            shared_words = new_words.intersection(existing_words)
            if len(shared_words) >= 2:
                return candidate

    return None
