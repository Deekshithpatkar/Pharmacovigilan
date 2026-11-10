from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_full_end_to_end_case_lifecycle():
    """
    Test complete lifecycle across all components:
    1. Submit an adverse event case
    2. AI information extraction & normalization
    3. Drug-label evidence retrieval
    4. Safety triage & duplicate detection
    5. Case routed to human review
    6. Reviewer views pending queue and adjudicates
    7. Verify permanent audit history
    """
    # Step 1: Submit a serious adverse event report
    report_payload = {
        "reporter_type": "pharmacist",
        "patient_age": 45,
        "patient_sex": "Male",
        "suspected_drug": "Amoxicillin",
        "reaction_description": "Patient developed acute dyspnoea, facial swelling, and anaphylaxis.",
        "outcome": "recovering"
    }
    submit_res = client.post("/cases", json=report_payload)
    assert submit_res.status_code == 201
    case_data = submit_res.json()
    case_id = case_data["case_id"]

    # Step 2 & 3 & 4: Verify extraction, triage, and routing
    assert case_data["status"] == "human_review"
    assert case_data["triage_priority"] == "URGENT"
    assert case_data["requires_human_review"] is True
    assert "Amoxicillin" in case_data["extracted_info"]["drugs"]
    assert len(case_data["evidence"]) > 0

    # Step 5: Verify case appears in Reviewer Queue
    pending_res = client.get("/review/pending")
    assert pending_res.status_code == 200
    pending_ids = [c["case_id"] for c in pending_res.json()]
    assert case_id in pending_ids

    # Step 6: Reviewer adjudicates and completes the case
    adjudicate_payload = {
        "reviewer_notes": "Adjudicated by Pharmacovigilance Officer. Anaphylactic reaction confirmed.",
        "adjudicated_status": "completed"
    }
    adj_res = client.post(f"/review/{case_id}/adjudicate", json=adjudicate_payload)
    assert adj_res.status_code == 200
    assert adj_res.json()["new_status"] == "completed"

    # Step 7: Verify status lookup and complete audit trail
    status_res = client.get(f"/cases/{case_id}")
    assert status_res.status_code == 200
    assert status_res.json()["status"] == "completed"

    audit_res = client.get(f"/cases/{case_id}/audit")
    assert audit_res.status_code == 200
    audit_logs = audit_res.json()
    assert len(audit_logs) >= 2
    actions = [log["action"] for log in audit_logs]
    assert "CASE_CREATED" in actions
    assert "CASE_ADJUDICATED" in actions

