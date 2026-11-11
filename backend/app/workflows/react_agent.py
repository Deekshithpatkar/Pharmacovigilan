import json
from typing import List, Dict, Any
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from app.config import settings
from app.ai.normalization import normalize_drug_name, standardize_reaction_term
from app.ai.label_retrieval import retrieve_label_evidence

# -------------------------------------------------------------
# 1. DEFINE TOOLS FOR THE REACT AGENT
# -------------------------------------------------------------
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
def evaluate_triage_rules_tool(severity_score: int, is_listed: bool, is_life_threatening: bool) -> str:
    """Evaluate deterministic safety triage rule based on severity score and label listing status."""
    if severity_score >= 4 or is_life_threatening:
        return "DECISION: Priority=URGENT, Route=HUMAN_REVIEW (Reason: High clinical severity or life-threatening event)"
    if not is_listed:
        return "DECISION: Priority=REVIEW_REQUIRED, Route=HUMAN_REVIEW (Reason: Unlisted reaction not in official label)"
    return "DECISION: Priority=ROUTINE, Route=COMPLETED (Reason: Mild known labeled adverse event)"

ALL_TOOLS = [
    normalize_drug_tool,
    standardize_symptom_tool,
    search_fda_label_evidence_tool,
    evaluate_triage_rules_tool
]

# -------------------------------------------------------------
# 2. CREATE THE REACT AGENT
# -------------------------------------------------------------
SYSTEM_PROMPT = """You are an expert Clinical Pharmacovigilance ReAct Agent.
Your job is to investigate adverse drug reports step-by-step:
1. Normalize the suspected drug using 'normalize_drug_tool'.
2. Standardize symptoms using 'standardize_symptom_tool'.
3. Search official FDA safety labels using 'search_fda_label_evidence_tool'.
4. Determine final safety triage using 'evaluate_triage_rules_tool'.

Think step-by-step. Formulate a Thought, call the necessary Tool (Action), observe the result (Observation), and then synthesize a clear clinical safety summary."""

def run_react_agent_investigation(
    suspected_drug: str,
    reaction_description: str,
    patient_info: str = "N/A"
) -> Dict[str, Any]:
    """Execute the full ReAct loop and return the chain-of-thought steps and final answer."""
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite",
        google_api_key=settings.gemini_api_key,
        api_version="v1beta",
        temperature=0.0
    )

    agent_executor = create_react_agent(llm, ALL_TOOLS)

    user_query = f"""Please investigate this adverse drug event report:
- Suspected Drug: {suspected_drug}
- Reaction Description: {reaction_description}
- Patient Info: {patient_info}
"""

    inputs = {"messages": [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=user_query)]}
    response = agent_executor.invoke(inputs)

    steps = []
    for msg in response["messages"]:
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                steps.append({
                    "type": "ACTION / TOOL_CALL",
                    "tool": tc["name"],
                    "args": tc["args"]
                })
        elif hasattr(msg, "name") and msg.name:
            steps.append({
                "type": "OBSERVATION",
                "tool": msg.name,
                "content": str(msg.content)
            })

    final_answer = response["messages"][-1].content

    return {
        "final_verdict": final_answer,
        "agent_steps": steps
    }
