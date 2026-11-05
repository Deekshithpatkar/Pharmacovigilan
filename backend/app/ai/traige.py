from typing import Optional, List
from pydantic import BaseModel
from app.ai.evidence_verification import VerificationResult

class TriageDecision(BaseModel):
    """Deterministic safety triage recommendation."""
    priority: str          # "URGENT", "REVIEW_REQUIRED", or "ROUTINE"
    requires_human_review: bool
    triage_reason: str
    recommended_action: str

# Serious reaction keywords requiring immediate escalation
SERIOUS_REACTION_KEYWORDS = [
    "death", "fatal", "anaphylaxis", "cardiac arrest",
    "seizure", "respiratory arrest", "organ failure", "coma"
]

def triage_case(
    severity: Optional[int],
    verification: VerificationResult,
    reactions: List[str]
) -> TriageDecision:
    """
    Apply deterministic safety triage rules:
    Rule 1 (Urgent): High severity (>= 4) or known life-threatening reaction.
    Rule 2 (Review Required): Unlisted / unknown reaction, or missing evidence.
    Rule 3 (Routine): Known, listed mild-to-moderate reaction (severity <= 3).
    """
    # 1. Check for life-threatening reaction keywords
    has_serious_keyword = any(
        any(kwd in rx.lower() for kwd in SERIOUS_REACTION_KEYWORDS)
        for rx in reactions
    )

    if (severity is not None and severity >= 4) or has_serious_keyword:
        return TriageDecision(
            priority="URGENT",
            requires_human_review=True,
            triage_reason="High clinical severity or life-threatening reaction reported.",
            recommended_action="Immediate escalation to medical safety officer."
        )

    # 2. Check for missing evidence or unlisted/unexpected reactions
    if not verification.evidence_found:
        return TriageDecision(
            priority="REVIEW_REQUIRED",
            requires_human_review=True,
            triage_reason="No official drug label evidence could be retrieved.",
            recommended_action="Manual verification of drug label by safety specialist."
        )

    if verification.unlisted_reactions:
        unlisted_str = ", ".join(verification.unlisted_reactions)
        return TriageDecision(
            priority="REVIEW_REQUIRED",
            requires_human_review=True,
            triage_reason=f"Unlisted reaction(s) not in official label: {unlisted_str}.",
            recommended_action="Route to human reviewer to assess potential new safety signal."
        )

    # 3. Known, mild-to-moderate reaction with complete evidence
    return TriageDecision(
        priority="ROUTINE",
        requires_human_review=False,
        triage_reason="Known labeled reaction with low to moderate severity.",
        recommended_action="Log case and continue standard periodic surveillance."
    )

