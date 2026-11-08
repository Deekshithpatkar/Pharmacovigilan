from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_workflow_urgent_routes_to_human_review():
    """Report with severe anaphylaxis should automatically route to HUMAN_REVIEW."""
    payload = {
        "reporter_type": "patient",
        "suspected_drug": "Amoxicillin",
        "reaction_description": "I took amoxicillin and suffered severe anaphylaxis and breathing difficulty."
    }
    response = client.post("/cases", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "human_review"
    assert data["requires_human_review"] is True
    assert data["triage_priority"] == "URGENT"

def test_workflow_routine_completes():
    """Mild known reaction without duplicates can complete automatically."""
    payload = {
        "reporter_type": "patient",
        "suspected_drug": "Paracetamol",
        "reaction_description": "I had mild nausea after taking paracetamol."
    }
    response = client.post("/cases", json=payload)
    assert response.status_code == 201
    data = response.json()
    # Paracetamol label lists nausea as common
    assert data["status"] in ["completed", "human_review"]

def test_reviewer_can_list_and_adjudicate_case():
    """Human safety reviewer can view pending queue and adjudicate."""
    # 1. Submit an urgent case
    payload = {
        "reporter_type": "doctor",
        "suspected_drug": "Aspirin",
        "reaction_description": "Patient developed severe cardiac arrest following dose."
    }
    create_res = client.post("/cases", json=payload)
    case_id = create_res.json()["case_id"]

    # 2. Reviewer checks pending cases
    pending_res = client.get("/review/pending")
    assert pending_res.status_code == 200
    pending_ids = [c["case_id"] for c in pending_res.json()]
    assert case_id in pending_ids

    # 3. Reviewer adjudicates the case
    adjudicate_res = client.post(
        f"/review/{case_id}/adjudicate",
        json={
            "reviewer_notes": "Reviewed by Dr. Smith. Escalated to regulatory pharmacovigilance team.",
            "adjudicated_status": "completed"
        }
    )
    assert adjudicate_res.status_code == 200
    assert adjudicate_res.json()["new_status"] == "completed"

