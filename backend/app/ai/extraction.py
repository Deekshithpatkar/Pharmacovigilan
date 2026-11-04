import json
from typing import List, Optional
import httpx
from pydantic import BaseModel, Field
from app.config import settings

class ExtractedCaseInfo(BaseModel):
    """Structured clinical information extracted from report text."""
    drugs: List[str] = Field(default_factory=list, description="Drugs mentioned")
    reactions: List[str] = Field(default_factory=list, description="Symptoms and adverse reactions")
    severity: int = Field(default=1, ge=1, le=5, description="Severity score 1-5")
    outcome: Optional[str] = Field(default=None, description="Reported outcome")

def _rule_based_extract(text: str, suspected_drug: Optional[str] = None) -> ExtractedCaseInfo:
    """Fast, deterministic fallback extractor that requires no network or API key."""
    text_lower = text.lower()

    # 1. Identify drugs
    drugs = []
    if suspected_drug and suspected_drug.strip():
        drugs.append(suspected_drug.strip().title())

    common_drugs = ["aspirin", "ibuprofen", "amoxicillin", "metformin", "paracetamol", "lisinopril", "atorvastatin"]
    for d in common_drugs:
        if d in text_lower and d.title() not in drugs:
            drugs.append(d.title())

    # 2. Identify reactions / symptoms
    common_reactions = [
        "rash", "itching", "hives", "headache", "nausea",
        "vomiting", "dizziness", "ulcer", "swelling", "fever",
        "anaphylaxis", "shortness of breath", "chest pain"
    ]
    reactions = [r for r in common_reactions if r in text_lower]

    # 3. Determine severity (1 = mildest, 5 = life-threatening)
    severity = 1
    if any(k in text_lower for k in ["anaphylaxis", "cardiac", "life-threatening", "fatal", "died"]):
        severity = 5
    elif any(k in text_lower for k in ["severe", "hospital", "hospitalization", "ulcer", "chest pain"]):
        severity = 4
    elif any(k in text_lower for k in ["moderate", "vomiting", "fever", "swelling", "dizziness"]):
        severity = 3
    elif any(k in text_lower for k in ["mild", "itching", "nausea", "headache", "rash"]):
        severity = 2

    # 4. Identify outcome
    outcome = None
    for term in ["recovering", "recovered", "not recovered", "fatal", "unknown"]:
        if term in text_lower:
            outcome = term
            break

    return ExtractedCaseInfo(
        drugs=drugs,
        reactions=reactions,
        severity=severity,
        outcome=outcome
    )

def extract_case_info(text: str, suspected_drug: Optional[str] = None) -> ExtractedCaseInfo:
    """Extract clinical entities using LLM (if configured) or smart local fallback."""
    if settings.gemini_api_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.gemini_api_key}"
            prompt = (
                f"Extract structured adverse event info from this report text.\n"
                f"Report text: {text}\n"
                f"Suspected drug: {suspected_drug or ''}\n\n"
                f"Output strictly valid JSON with keys: drugs (list), reactions (list), severity (int 1-5), outcome (str or null)."
            )
            resp = httpx.post(
                url,
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"response_mime_type": "application/json"}
                },
                timeout=10.0
            )
            if resp.status_code == 200:
                raw_json = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                return ExtractedCaseInfo(**json.loads(raw_json))
        except Exception:
            pass  # Fall back seamlessly if network is unavailable or API key is invalid

    return _rule_based_extract(text, suspected_drug)
