from typing import List
from pydantic import BaseModel
from app.ai.label_retrieval import LabelEvidence

class VerificationResult(BaseModel):
    """Summary of whether reported reactions are confirmed in the official drug label."""
    all_reactions_listed: bool
    listed_reactions: List[str]
    unlisted_reactions: List[str]
    evidence_found: bool

def verify_reactions_against_evidence(
    reaction_terms: List[str],
    evidence_list: List[LabelEvidence]
) -> VerificationResult:
    """Check which reactions are listed in retrieved evidence and which are unlisted."""
    if not evidence_list:
        return VerificationResult(
            all_reactions_listed=False,
            listed_reactions=[],
            unlisted_reactions=reaction_terms,
            evidence_found=False
        )

    listed = []
    unlisted = []

    for term in reaction_terms:
        # A reaction is considered listed if any retrieved evidence confirms it
        is_term_listed = any(
            ev.matched_term.lower() == term.lower() and ev.is_listed
            for ev in evidence_list
        )
        if is_term_listed:
            listed.append(term)
        else:
            unlisted.append(term)

    return VerificationResult(
        all_reactions_listed=len(unlisted) == 0 and len(listed) > 0,
        listed_reactions=listed,
        unlisted_reactions=unlisted,
        evidence_found=True
    )

