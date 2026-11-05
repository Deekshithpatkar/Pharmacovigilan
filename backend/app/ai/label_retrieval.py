import json
from pathlib import Path
from typing import List, Optional
import httpx
from pydantic import BaseModel
from app.ai.normalization import normalize_drug_name

DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data" / "drug_labels"

class LabelEvidence(BaseModel):
    """Traceable evidence snippet from an official drug label."""
    drug_name: str
    source: str
    version_date: str
    section: str
    matched_term: str
    passage: str
    is_listed: bool

def load_drug_label(drug_name: str) -> Optional[dict]:
    """Load official drug label from local data store or live openFDA."""
    normalized = normalize_drug_name(drug_name).lower()
    local_file = DATA_DIR / f"{normalized}.json"

    # 1. Check local versioned data store
    if local_file.exists():
        with open(local_file, "r", encoding="utf-8") as f:
            return json.load(f)

    # 2. Live openFDA API fallback if not in local store
    try:
        url = f"https://api.fda.gov/drug/label.json?search=openfda.generic_name:\"{normalized}\"&limit=1"
        res = httpx.get(url, timeout=5.0)
        if res.status_code == 200:
            results = res.json().get("results", [])
            if results:
                label_data = results[0]
                return {
                    "drug_name": normalize_drug_name(drug_name),
                    "source": "openFDA REST API",
                    "version_date": label_data.get("effective_time", "Unknown"),
                    "adverse_reactions": " ".join(label_data.get("adverse_reactions", [])),
                    "warnings": " ".join(label_data.get("warnings_and_cautions", label_data.get("warnings", []))),
                }
    except Exception:
        pass  # Graceful fallback if offline or API is down

    return None

def retrieve_label_evidence(drug_name: str, reaction_terms: List[str]) -> List[LabelEvidence]:
    """Retrieve drug-label evidence for given reactions with traceable sources."""
    label = load_drug_label(drug_name)
    if not label:
        return []

    evidence_list: List[LabelEvidence] = []
    adverse_text = label.get("adverse_reactions", "")
    warnings_text = label.get("warnings", "")

    for term in reaction_terms:
        term_clean = term.strip().lower()
        matched = False

        # Check adverse reactions section
        if term_clean in adverse_text.lower():
            evidence_list.append(LabelEvidence(
                drug_name=label["drug_name"],
                source=label["source"],
                version_date=label["version_date"],
                section="adverse_reactions",
                matched_term=term,
                passage=adverse_text,
                is_listed=True
            ))
            matched = True

        # Check warnings section
        if term_clean in warnings_text.lower():
            evidence_list.append(LabelEvidence(
                drug_name=label["drug_name"],
                source=label["source"],
                version_date=label["version_date"],
                section="warnings",
                matched_term=term,
                passage=warnings_text,
                is_listed=True
            ))
            matched = True

        # If not found in either section, record as unlisted (uncertain)
        if not matched:
            evidence_list.append(LabelEvidence(
                drug_name=label["drug_name"],
                source=label["source"],
                version_date=label["version_date"],
                section="not_found",
                matched_term=term,
                passage="Term not found in retrieved drug label passages.",
                is_listed=False
            ))

    return evidence_list

