from typing import List

# 1. Drug Normalization Dictionary (Brand name / synonym -> Standardized Generic INN name)
DRUG_SYNONYMS = {
    # Acetaminophen / Paracetamol
    "tylenol": "Paracetamol",
    "panadol": "Paracetamol",
    "acetaminophen": "Paracetamol",
    "paracetamol": "Paracetamol",
    "calpol": "Paracetamol",
    # Ibuprofen
    "advil": "Ibuprofen",
    "motrin": "Ibuprofen",
    "nurofen": "Ibuprofen",
    "ibuprofen": "Ibuprofen",
    # Aspirin
    "aspirin": "Aspirin",
    "bayer": "Aspirin",
    "disprin": "Aspirin",
    "acetylsalicylic acid": "Aspirin",
    # Amoxicillin
    "amoxil": "Amoxicillin",
    "amoxicillin": "Amoxicillin",
    "augmentin": "Amoxicillin-Clavulanate",
    # Metformin
    "glucophage": "Metformin",
    "metformin": "Metformin",
    # Atorvastatin
    "lipitor": "Atorvastatin",
    "atorvastatin": "Atorvastatin",
    # Lisinopril
    "zestril": "Lisinopril",
    "prinivil": "Lisinopril",
    "lisinopril": "Lisinopril",
}

# 2. Standardized Reaction Terminology (Colloquial symptom -> Medical Preferred Term / MedDRA PT)
REACTION_TERMS = {
    "itching": "Pruritus",
    "itchy": "Pruritus",
    "hives": "Urticaria",
    "rash": "Rash",
    "skin rash": "Rash",
    "headache": "Headache",
    "head hurt": "Headache",
    "nausea": "Nausea",
    "queasy": "Nausea",
    "vomiting": "Vomiting",
    "throwing up": "Vomiting",
    "dizziness": "Dizziness",
    "lightheaded": "Dizziness",
    "swelling": "Oedema",
    "facial swelling": "Facial oedema",
    "swollen face": "Facial oedema",
    "shortness of breath": "Dyspnoea",
    "trouble breathing": "Dyspnoea",
    "breathless": "Dyspnoea",
    "ulcer": "Gastric ulcer",
    "fever": "Pyrexia",
    "high temp": "Pyrexia",
    "anaphylaxis": "Anaphylactic reaction",
    "allergic shock": "Anaphylactic reaction",
    "chest pain": "Chest pain",
    "hair loss": "Alopecia",
}

def normalize_drug_name(raw_name: str) -> str:
    """Normalize a brand name, trade name, or colloquial drug name to its generic INN name."""
    if not raw_name:
        return ""
    cleaned = raw_name.strip().lower()
    return DRUG_SYNONYMS.get(cleaned, raw_name.strip().title())

def standardize_reaction_term(raw_reaction: str) -> str:
    """Map a single colloquial reaction term to its standardized MedDRA Preferred Term."""
    if not raw_reaction:
        return ""
    cleaned = raw_reaction.strip().lower()
    return REACTION_TERMS.get(cleaned, raw_reaction.strip().title())

def normalize_reaction_terms(raw_reactions: List[str]) -> List[str]:
    """Map colloquial reaction terms to standardized clinical Preferred Terms (e.g. MedDRA PT)."""
    normalized = []
    for reaction in raw_reactions:
        cleaned = reaction.strip().lower()
        term = REACTION_TERMS.get(cleaned, reaction.strip().title())
        if term not in normalized:
            normalized.append(term)
    return normalized

