from typing import List
from pydantic import BaseModel
from app.api.schemas.case import AdverseEventCaseCreate, CaseStatus
from app.ai.extraction import ExtractedCaseInfo
from app.ai.label_retrieval import LabelEvidence
from app.ai.evidence_verification import VerificationResult, verify_reactions_against_evidence
from app.ai.traige import TriageDecision, triage_case

class CaseWorkflowResult(BaseModel):
    """Complete result of running an adverse event case through the workflow."""
    final_status: CaseStatus
    extracted_info: ExtractedCaseInfo
    evidence: List[LabelEvidence]
    verification: VerificationResult
    triage: TriageDecision
    route_to_human_reviewer: bool
    review_reason: str

def run_case_workflow(
    case_data: AdverseEventCaseCreate,
    is_duplicate: bool,
    extracted_info: ExtractedCaseInfo,
    evidence: List[LabelEvidence]
) -> CaseWorkflowResult:
    """
    Orchestrate the case workflow and route for human review:
    1. If duplicate -> route to human review.
    2. Verify reactions against official drug label evidence.
    3. Apply triage rules (Urgent, Review Required, Routine).
    4. Determine final case status.
    """
    # 1. Check duplicate routing first
    if is_duplicate:
        verification = verify_reactions_against_evidence(
            extracted_info.reactions, evidence
        )
        triage = TriageDecision(
            priority="REVIEW_REQUIRED",
            requires_human_review=True,
            triage_reason="Potential duplicate of an existing case.",
            recommended_action="Safety officer needs to confirm or merge duplicate case."
        )
        return CaseWorkflowResult(
            final_status=CaseStatus.HUMAN_REVIEW,
            extracted_info=extracted_info,
            evidence=evidence,
            verification=verification,
            triage=triage,
            route_to_human_reviewer=True,
            review_reason="Potential duplicate case detected."
        )

    # 2. Evidence verification
    search_terms = list(set(extracted_info.reactions + extracted_info.standardized_reactions))
    verification = verify_reactions_against_evidence(search_terms, evidence)

    # 3. Deterministic Safety Triage
    triage = triage_case(
        severity=extracted_info.severity,
        verification=verification,
        reactions=search_terms
    )

    # 4. Routing condition
    if triage.requires_human_review:
        final_status = CaseStatus.HUMAN_REVIEW
        route_to_human = True
        review_reason = f"[{triage.priority}] {triage.triage_reason}"
    else:
        final_status = CaseStatus.COMPLETED
        route_to_human = False
        review_reason = "No human review required. Case completed automatically."

    return CaseWorkflowResult(
        final_status=final_status,
        extracted_info=extracted_info,
        evidence=evidence,
        verification=verification,
        triage=triage,
        route_to_human_reviewer=route_to_human,
        review_reason=review_reason
    )

