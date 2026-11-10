import pytest
from datetime import date
from pydantic import ValidationError
from app.api.schemas.case import AdverseEventCaseCreate, ReporterType

def test_validation_valid_case():
    """Valid report should pass schema validation without errors."""
    case = AdverseEventCaseCreate(
        reporter_type=ReporterType.PATIENT,
        suspected_drug="Amoxicillin",
        reaction_description="Mild rash developed on arms after taking medication.",
        patient_age=30,
        patient_sex="Female"
    )
    assert case.suspected_drug == "Amoxicillin"
    assert case.patient_age == 30

def test_validation_missing_suspected_drug():
    """Missing or empty suspected drug should raise ValidationError."""
    with pytest.raises(ValidationError):
        AdverseEventCaseCreate(
            reporter_type=ReporterType.PATIENT,
            suspected_drug="",  # min_length=1
            reaction_description="Felt dizzy and nauseous."
        )

def test_validation_short_reaction_description():
    """Reaction description shorter than 5 chars should fail validation."""
    with pytest.raises(ValidationError):
        AdverseEventCaseCreate(
            reporter_type=ReporterType.PATIENT,
            suspected_drug="Metformin",
            reaction_description="Bad"  # min_length=5
        )

def test_validation_invalid_patient_age():
    """Negative age or age > 130 should fail validation."""
    with pytest.raises(ValidationError):
        AdverseEventCaseCreate(
            reporter_type=ReporterType.DOCTOR,
            suspected_drug="Aspirin",
            reaction_description="Patient experienced stomach pain.",
            patient_age=-5
        )

def test_validation_reaction_date_before_drug_date():
    """Reaction start date cannot be before drug start date."""
    with pytest.raises(ValidationError, match="reaction start date cannot be before drug start date"):
        AdverseEventCaseCreate(
            reporter_type=ReporterType.PATIENT,
            suspected_drug="Ibuprofen",
            reaction_description="Headache and rash after taking drug.",
            drug_start_date=date(2024, 5, 10),
            reaction_start_date=date(2024, 5, 1)  # Invalid: before drug start date
        )

