from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_case_creation_and_review_generates_audit_logs():
    """Verify that case creation and reviewer adjudication produce immutable audit logs."""
    # 1. Submit a case
    payload = {
        "reporter_type": "nurse",
        "suspected_drug": "Amoxicillin",
        "reaction_description": "Patient developed severe anaphylaxis and dyspnoea."
    }
    create_res = client.post("/cases", json=payload)
    assert create_res.status_code == 201
    case_id = create_res.json()["case_id"]

    # 2. Check initial audit log for creation
    audit_res = client.get(f"/cases/{case_id}/audit")
    assert audit_res.status_code == 200
    logs = audit_res.json()
    assert len(logs) >= 1
    assert logs[0]["action"] == "CASE_CREATED"
    assert logs[0]["actor"] == "nurse"
    assert logs[0]["new_status"] == "human_review"

    # 3. Adjudicate the case (with reviewer key)
    headers = {"X-Reviewer-Key": "med_safety_2026"}
    adj_res = client.post(
        f"/review/{case_id}/adjudicate",
        headers=headers,
        json={
            "reviewer_notes": "Allergy confirmed. Epinephrine administered.",
            "adjudicated_status": "completed"
        }
    )
    assert adj_res.status_code == 200

    # 4. Check audit log has recorded the adjudication
    audit_res2 = client.get(f"/cases/{case_id}/audit")
    assert audit_res2.status_code == 200
    logs2 = audit_res2.json()
    assert len(logs2) == 2
    assert logs2[1]["action"] == "CASE_ADJUDICATED"
    assert logs2[1]["actor"] == "SAFETY_OFFICER"
    assert logs2[1]["previous_status"] == "human_review"
    assert logs2[1]["new_status"] == "completed"

