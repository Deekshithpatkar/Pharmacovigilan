import pytest
from pydantic import ValidationError
from app.api.schemas.case import(
    AdverseEventCaseCreate, ReporterType,
)

def test_valid_case():
    case=AdverseEventCaseCreate(
        reporter_type=ReporterType.DOCTOR,
        suspected_drug="Example medicine",
        reaction_description="Patient developed a skin rash",
    )
    assert case.suspected_drug == "Example medicine"


def test_empty_drug_rejected():
    with pytest.raises(ValidationError):
        AdverseEventCaseCreate(
            reporter_type=ReporterType.DOCTOR,
            suspected_drug="",
            reaction_description="Patient developed skin rash",
        )

def test_invalid_age_rejection():
    with pytest.raises(ValidationError):
        AdverseEventCaseCreate(
            reporter_type=ReporterType.DOCTOR,
            patient_age=150,
            suspected_drug="Example medicine",
            reaction_description="Patient developed a skin rash",
        )
    
def test_reaction_before_drug_start_rejected():
    with pytest.raises(ValidationError):
        AdverseEventCaseCreate(
            reporter_type=ReporterType.DOCTOR,
            suspected_drug="Example medicine",
            reaction_description="Patient developed a skin rash",
            drug_start_date="2026-10-20",
            reaction_start_date="2026-10-18",
        )