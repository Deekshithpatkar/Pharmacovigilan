import pytest
from pydantic import ValidationError
from app.ai.extraction import extract_case_info, ExtractedCaseInfo
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_extract_mild_symptoms():
    text = "Patient took Paracetamol and noticed mild nausea and headache. Recovering well."
    info = extract_case_info(text=text, suspected_drug="Paracetamol")

    assert "Paracetamol" in info.drugs
    assert "nausea" in info.reactions
    assert "headache" in info.reactions
    assert info.severity == 2
    assert info.outcome == "recovering"

def test_extract_life_threatening_symptoms():
    text = "Patient suffered severe anaphylaxis and shortness of breath after taking Ibuprofen."
    info = extract_case_info(text=text, suspected_drug="Ibuprofen")

    assert "Ibuprofen" in info.drugs
    assert "anaphylaxis" in info.reactions
    assert "shortness of breath" in info.reactions
    assert info.severity == 5

def test_extracted_info_in_api_response():
    payload = {
        "reporter_type": "doctor",
        "suspected_drug": "Amoxicillin",
        "reaction_description": "Patient developed severe rash and facial swelling",
    }
    response = client.post("/cases", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "extracted_info" in data
    assert "Amoxicillin" in data["extracted_info"]["drugs"]
    assert "rash" in data["extracted_info"]["reactions"]
    assert "swelling" in data["extracted_info"]["reactions"]
    assert data["extracted_info"]["severity"] >= 3

def test_invalid_severity_raises_validation_error():
    with pytest.raises(ValidationError):
        ExtractedCaseInfo(severity=10)  # ge=1, le=5
