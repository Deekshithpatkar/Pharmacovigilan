from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_duplicate_detection_and_linking():
    # 1. Submit initial report
    first_report = {
        "reporter_type": "doctor",
        "patient_age": 52,
        "patient_sex": "male",
        "suspected_drug": "Aspirin",
        "reaction_description": "Patient developed severe skin rash and itching",
    }
    first_res = client.post("/cases", json=first_report)
    assert first_res.status_code == 201
    first_data = first_res.json()
    assert first_data["status"] == "submitted"
    assert first_data["duplicate_of"] is None
    original_case_id = first_data["case_id"]

    # 2. Submit second report with same drug, age, sex, and overlapping symptoms
    duplicate_report = {
        "reporter_type": "nurse",
        "patient_age": 52,
        "patient_sex": "male",
        "suspected_drug": "aspirin",  # case-insensitive match
        "reaction_description": "Noticed skin rash and itching on arms",
    }
    dup_res = client.post("/cases", json=duplicate_report)
    assert dup_res.status_code == 201
    dup_data = dup_res.json()
    # It must be linked to the original case and routed to human review!
    assert dup_data["status"] == "human_review"
    assert dup_data["duplicate_of"] == original_case_id
    assert "Possible duplicate detected" in dup_data["message"]

    # 3. Submit different report (different drug and patient)
    different_report = {
        "reporter_type": "patient",
        "patient_age": 28,
        "patient_sex": "female",
        "suspected_drug": "Metformin",
        "reaction_description": "Mild stomach upset and nausea",
    }
    diff_res = client.post("/cases", json=different_report)
    assert diff_res.status_code == 201
    diff_data = diff_res.json()
    assert diff_data["status"] == "submitted"
    assert diff_data["duplicate_of"] is None
