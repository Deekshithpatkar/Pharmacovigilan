from app.ai.label_retrieval import load_drug_label, retrieve_label_evidence
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_load_drug_label():
    label = load_drug_label("Amoxicillin")
    assert label is not None
    assert label["drug_name"] == "Amoxicillin"
    assert "2024" in label["version_date"]
    assert "adverse_reactions" in label

def test_retrieve_known_reaction_evidence():
    evidence = retrieve_label_evidence("Amoxicillin", ["rash"])
    assert len(evidence) >= 1
    ev = evidence[0]
    assert ev.drug_name == "Amoxicillin"
    assert ev.is_listed is True
    assert ev.section == "adverse_reactions"
    assert "skin rash" in ev.passage
    assert ev.version_date == "2024-03-01"

def test_retrieve_warning_evidence():
    evidence = retrieve_label_evidence("Amoxicillin", ["anaphylaxis"])
    # Anaphylaxis is mentioned in adverse_reactions and warnings
    sections = [e.section for e in evidence if e.is_listed]
    assert "warnings" in sections or "adverse_reactions" in sections

def test_retrieve_unlisted_reaction():
    evidence = retrieve_label_evidence("Amoxicillin", ["hallucinations"])
    assert len(evidence) == 1
    assert evidence[0].is_listed is False
    assert evidence[0].section == "not_found"

def test_evidence_in_api_response():
    res = client.post("/cases", json={
        "reporter_type": "patient",
        "suspected_drug": "Ibuprofen",
        "reaction_description": "Experienced severe dizziness and vomiting",
    })
    assert res.status_code == 201
    data = res.json()
    assert "evidence" in data
    assert len(data["evidence"]) > 0
    # Ibuprofen label lists dizziness and vomiting
    listed_sections = [e for e in data["evidence"] if e["is_listed"]]
    assert len(listed_sections) > 0

