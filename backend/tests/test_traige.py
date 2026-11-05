from app.ai.label_retrieval import LabelEvidence
from app.ai.evidence_verification import verify_reactions_against_evidence
from app.ai.traige import triage_case

def test_verify_reactions_listed_and_unlisted():
    evidence = [
        LabelEvidence(
            drug_name="Amoxicillin",
            source="FDA",
            version_date="2024",
            section="adverse_reactions",
            matched_term="rash",
            passage="Common: rash, diarrhea",
            is_listed=True
        ),
        LabelEvidence(
            drug_name="Amoxicillin",
            source="FDA",
            version_date="2024",
            section="not_found",
            matched_term="hallucinations",
            passage="Not found",
            is_listed=False
        )
    ]
    res = verify_reactions_against_evidence(["rash", "hallucinations"], evidence)
    assert res.all_reactions_listed is False
    assert "rash" in res.listed_reactions
    assert "hallucinations" in res.unlisted_reactions

def test_triage_urgent_high_severity():
    evidence = [
        LabelEvidence(
            drug_name="Aspirin", source="FDA", version_date="2024",
            section="adverse_reactions", matched_term="nausea", passage="nausea", is_listed=True
        )
    ]
    verif = verify_reactions_against_evidence(["nausea"], evidence)
    decision = triage_case(severity=5, verification=verif, reactions=["nausea"])
    assert decision.priority == "URGENT"
    assert decision.requires_human_review is True

def test_triage_review_required_unlisted_reaction():
    evidence = [
        LabelEvidence(
            drug_name="Amoxicillin", source="FDA", version_date="2024",
            section="not_found", matched_term="hair loss", passage="Not found", is_listed=False
        )
    ]
    verif = verify_reactions_against_evidence(["hair loss"], evidence)
    decision = triage_case(severity=2, verification=verif, reactions=["hair loss"])
    assert decision.priority == "REVIEW_REQUIRED"
    assert decision.requires_human_review is True

def test_triage_routine_known_mild_reaction():
    evidence = [
        LabelEvidence(
            drug_name="Paracetamol", source="FDA", version_date="2024",
            section="adverse_reactions", matched_term="nausea", passage="nausea", is_listed=True
        )
    ]
    verif = verify_reactions_against_evidence(["nausea"], evidence)
    decision = triage_case(severity=2, verification=verif, reactions=["nausea"])
    assert decision.priority == "ROUTINE"
    assert decision.requires_human_review is False

