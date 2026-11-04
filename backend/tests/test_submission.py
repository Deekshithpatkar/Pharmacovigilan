from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_submit_valid_case():
    payload = {
        "reporter_type": "doctor",
        "patient_age": 45,
        "patient_sex": "male",
        "suspected_drug": "Ibuprofen",
        "reaction_description": "Patient developed acute stomach ulcers after 3 days",
        "drug_start_date": "2026-10-01",
        "reaction_start_date": "2026-10-04",
        "outcome": "recovering"
    }
    response = client.post("/cases", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["case_id"].startswith("PV-")
    assert data["status"] == "submitted"
    assert "submitted successfully" in data["message"]

    # Verify we can retrieve it by the returned case_id
    get_response = client.get(f"/cases/{data['case_id']}")
    assert get_response.status_code == 200
    assert get_response.json()["case_id"] == data["case_id"]

def test_submit_invalid_case_missing_required_fields():
    # Missing suspected_drug and reaction_description
    payload = {
        "reporter_type": "patient"
    }
    response = client.post("/cases", json=payload)
    assert response.status_code == 422

def test_get_nonexistent_case():
    response = client.get("/cases/PV-NONEXISTENT")
    assert response.status_code == 404
