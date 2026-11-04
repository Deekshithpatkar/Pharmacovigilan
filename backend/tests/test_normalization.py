from app.ai.normalization import normalize_drug_name, normalize_reaction_terms
from app.ai.extraction import extract_case_info
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_normalize_drug_names():
    assert normalize_drug_name("tylenol") == "Paracetamol"
    assert normalize_drug_name("Advil") == "Ibuprofen"
    assert normalize_drug_name("Lipitor") == "Atorvastatin"
    assert normalize_drug_name("Glucophage") == "Metformin"
    assert normalize_drug_name("UnknownMed") == "Unknownmed"

def test_normalize_reaction_terms():
    raw_symptoms = ["hives", "trouble breathing", "itching", "fever"]
    standardized = normalize_reaction_terms(raw_symptoms)
    assert "Urticaria" in standardized
    assert "Dyspnoea" in standardized
    assert "Pruritus" in standardized
    assert "Pyrexia" in standardized

def test_extraction_includes_normalized_fields():
    text = "Patient took Tylenol and experienced hives and shortness of breath."
    info = extract_case_info(text=text, suspected_drug="Tylenol")
    assert "Paracetamol" in info.normalized_drugs
    assert "Urticaria" in info.standardized_reactions
    assert "Dyspnoea" in info.standardized_reactions

def test_duplicate_detection_across_brand_names():
    # Report 1 uses brand name 'Tylenol'
    r1 = client.post("/cases", json={
        "reporter_type": "doctor",
        "patient_age": 40,
        "patient_sex": "female",
        "suspected_drug": "Tylenol",
        "reaction_description": "Patient developed severe rash and facial swelling",
    })
    assert r1.status_code == 201
    case1_id = r1.json()["case_id"]

    # Report 2 uses generic name 'Paracetamol' for same patient
    r2 = client.post("/cases", json={
        "reporter_type": "nurse",
        "patient_age": 40,
        "patient_sex": "female",
        "suspected_drug": "Paracetamol",
        "reaction_description": "Severe rash and facial swelling on cheeks",
    })
    assert r2.status_code == 201
    r2_data = r2.json()
    # It catches it as a duplicate even though one said Tylenol and the other said Paracetamol!
    assert r2_data["status"] == "human_review"
    assert r2_data["duplicate_of"] == case1_id
