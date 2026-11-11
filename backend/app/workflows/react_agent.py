import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from app.config import settings
from app.api.schemas.case import AdverseEventCaseCreate, CaseStatus
from app.models.case import CaseModel
from app.services.duplicate_service import find_duplicate_case
from app.services.audit_service import record_audit_log
from app.ai.normalization import normalize_drug_name, standardize_reaction_term
from app.ai.label_retrieval import retrieve_label_evidence

# -------------------------------------------------------------
# 1. TOOL FACTORY (PROVIDES DB-AWARE & DOMAIN TOOLS)
# -------------------------------------------------------------
def build_agent_tools(db: Session, case_data: AdverseEventCaseCreate):
    """Build dynamic ReAct tools bound to the current database session and case data."""

    @tool
    def check_duplicate_cases_tool() -> str:
        """Search the safety database to check if this patient and drug already have an existing adverse report."""
        dup = find_duplicate_case(db, case_data)
        if dup:
            return f"POTENTIAL_DUPLICATE: Found matching existing Case ID '{dup.case_id}' (Drug: {dup.suspected_drug}, Status: {dup.status})."
        return "NO_DUPLICATE: No existing matching cases found in database."

    @tool
    def normalize_drug_tool(drug_name: str) -> str:
        """Standardize brand/trade name into official generic INN active ingredient (e.g. Tylenol -> Paracetamol)."""
        return normalize_drug_name(drug_name)

    @tool
    def standardize_symptom_tool(symptom: str) -> str:
        """Map reported colloquial symptom into standard MedDRA Preferred Term (e.g. hives -> Urticaria)."""
        return standardize_reaction_term(symptom)

    @tool
    def search_fda_label_evidence_tool(drug_name: str, reaction: str) -> str:
        """Search official FDA drug safety labels to check if an adverse reaction is documented/listed."""
        evidence = retrieve_label_evidence(drug_name, [reaction])
        if not evidence:
            return f"No official FDA label found for {drug_name}."
        ev = evidence[0]
        if ev.is_listed:
            return f"LISTED in FDA label section '{ev.section}': {ev.passage[:200]}..."
        return f"UNLISTED: '{reaction}' was NOT found in official FDA label passages for {drug_name}."

    @tool
    def evaluate_triage_rules_tool(severity_score: int, is_listed: bool, is_life_threatening: bool, is_duplicate: bool) -> str:
        """Evaluate deterministic safety triage rule based on severity score, duplicate status, and label listing status."""
        if is_duplicate:
            return "DECISION: Priority=REVIEW_REQUIRED, Route=HUMAN_REVIEW (Reason: Potential duplicate report detected)"
        if severity_score >= 4 or is_life_threatening:
            return "DECISION: Priority=URGENT, Route=HUMAN_REVIEW (Reason: High clinical severity or life-threatening event)"
        if not is_listed:
            return "DECISION: Priority=REVIEW_REQUIRED, Route=HUMAN_REVIEW (Reason: Unlisted reaction not in official label)"
        return "DECISION: Priority=ROUTINE, Route=COMPLETED (Reason: Mild known labeled adverse event)"

    return [
        check_duplicate_cases_tool,
        normalize_drug_tool,
        standardize_symptom_tool,
        search_fda_label_evidence_tool,
        evaluate_triage_rules_tool
    ]

# -------------------------------------------------------------
# 2. REACT AGENT RUNNER WITH DB PERSISTENCE
# -------------------------------------------------------------
SYSTEM_PROMPT = """You are an expert Clinical Pharmacovigilance ReAct Agent.
Your job is to investigate adverse drug reports step-by-step:
1. ALWAYS start by checking for duplicate records using 'check_duplicate_cases_tool'.
2. Normalize the suspected drug using 'normalize_drug_tool'.
3. Standardize symptoms using 'standardize_symptom_tool'.
4. Search official FDA safety labels using 'search_fda_label_evidence_tool'.
5. Determine final safety triage using 'evaluate_triage_rules_tool'.

Think step-by-step. Formulate a Thought, call the necessary Tool (Action), observe the result (Observation), and then synthesize a clear clinical safety summary."""

def run_react_agent_investigation(
    db: Session,
    case_data: AdverseEventCaseCreate
) -> Dict[str, Any]:
    """Execute the full ReAct loop, persist the case to PostgreSQL, and write audit trail."""
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite",
        google_api_key=settings.gemini_api_key,
        api_version="v1beta",
        temperature=0.0
    )

    tools = build_agent_tools(db, case_data)
    agent_executor = create_react_agent(llm, tools)

    user_query = f"""Please investigate this adverse drug event report:
- Suspected Drug: {case_data.suspected_drug}
- Reaction Description: {case_data.reaction_description}
- Patient Info: Age: {case_data.patient_age}, Sex: {case_data.patient_sex}
"""

    inputs = {"messages": [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=user_query)]}
    response = agent_executor.invoke(inputs)

    steps = []
    is_duplicate = False
    duplicate_of_id = None
    priority = "ROUTINE"
    final_status = CaseStatus.COMPLETED

    for msg in response["messages"]:
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                steps.append({
                    "type": "ACTION / TOOL_CALL",
                    "tool": tc["name"],
                    "args": tc["args"]
                })
        elif hasattr(msg, "name") and msg.name:
            content_str = str(msg.content)
            steps.append({
                "type": "OBSERVATION",
                "tool": msg.name,
                "content": content_str
            })
            if "POTENTIAL_DUPLICATE" in content_str:
                is_duplicate = True
                # Extract Case ID if present
                if "Case ID '" in content_str:
                    duplicate_of_id = content_str.split("Case ID '")[1].split("'")[0]
            if "Priority=URGENT" in content_str:
                priority = "URGENT"
                final_status = CaseStatus.HUMAN_REVIEW
            elif "Priority=REVIEW_REQUIRED" in content_str or is_duplicate:
                priority = "REVIEW_REQUIRED"
                final_status = CaseStatus.HUMAN_REVIEW

    raw_final = response["messages"][-1].content
    if isinstance(raw_final, list):
        final_answer = "".join(part.get("text", "") if isinstance(part, dict) else str(part) for part in raw_final)
    else:
        final_answer = str(raw_final)

    # -------------------------------------------------------------
    # 3. SAVE CASE TO DATABASE & LOG AUDIT TRAIL
    # -------------------------------------------------------------
    case_id = f"PV-{uuid.uuid4().hex[:8].upper()}"
    db_case = CaseModel(
        case_id=case_id,
        reporter_type=case_data.reporter_type.value,
        patient_age=case_data.patient_age,
        patient_sex=case_data.patient_sex,
        suspected_drug=case_data.suspected_drug,
        reaction_description=case_data.reaction_description,
        drug_start_date=case_data.drug_start_date,
        reaction_start_date=case_data.reaction_start_date,
        outcome=case_data.outcome,
        additional_information=case_data.additional_information,
        status=final_status.value,
        severity=5 if priority == "URGENT" else (3 if priority == "REVIEW_REQUIRED" else 1),
        duplicate_of_id=duplicate_of_id
    )
    db.add(db_case)
    db.commit()
    db.refresh(db_case)

    # Record Audit Log
    record_audit_log(
        db=db,
        case_id=db_case.case_id,
        action="REACT_AGENT_INVESTIGATED",
        new_status=db_case.status,
        actor="REACT_AGENT_AI",
        details=f"Investigated by ReAct agent. Priority: {priority}. Duplicate: {is_duplicate}"
    )

    return {
        "case_id": db_case.case_id,
        "status": db_case.status,
        "is_duplicate": is_duplicate,
        "duplicate_of": duplicate_of_id,
        "priority": priority,
        "final_verdict": final_answer.strip(),
        "agent_steps": steps
    }
