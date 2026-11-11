from app.workflows.react_agent import run_react_agent_investigation

def test_react_agent_execution():
    """Verify that the ReAct agent executes tool calls and synthesizes a verdict."""
    result = run_react_agent_investigation(
        suspected_drug="Amoxicillin",
        reaction_description="Patient developed severe hives and difficulty breathing.",
        patient_info="Age: 45, Sex: Male"
    )

    assert "final_verdict" in result
    assert "agent_steps" in result
    assert len(result["agent_steps"]) > 0

    # Verify that the agent called at least one of our domain tools
    tool_names = [step["tool"] for step in result["agent_steps"] if "tool" in step]
    assert any("tool" in t.lower() for t in tool_names)

