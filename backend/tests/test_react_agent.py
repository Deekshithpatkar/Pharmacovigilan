from app.database import SessionLocal
from app.api.schemas.case import AdverseEventCaseCreate, ReporterType
from app.workflows.react_agent import run_react_agent_investigation

def test_react_agent_duplicate_check_and_saving():
    """Verify ReAct agent calls check_duplicate_cases_tool and persists to DB."""
    db = SessionLocal()
    try:
        case_data = AdverseEventCaseCreate(
            reporter_type=ReporterType.PATIENT,
            patient_age=50,
            patient_sex="Female",
            suspected_drug="Amoxicillin",
            reaction_description="Patient developed severe hives and shortness of breath."
        )

        # 1. First run: Should create a new unique case
        res1 = run_react_agent_investigation(db, case_data)
        assert res1["case_id"].startswith("PV-")
        assert res1["is_duplicate"] is False

        # 2. Second run: Exact same report -> ReAct agent should catch the duplicate!
        res2 = run_react_agent_investigation(db, case_data)
        assert res2["case_id"].startswith("PV-")
        assert res2["is_duplicate"] is True
        assert res2["duplicate_of"] == res1["case_id"]
    finally:
        db.close()
