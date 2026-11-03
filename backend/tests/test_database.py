from app.database import engine, Base, SessionLocal
from app.models.case import CaseModel

def test_create_and_read_case():
    # 1. Create table in database
    Base.metadata.create_all(bind=engine)

    # 2. Insert a new case
    db = SessionLocal()
    new_case = CaseModel(
        case_id="CASE-1001",
        reporter_type="doctor",
        suspected_drug="Amoxicillin",
        reaction_description="Mild skin rash on torso",
        status="submitted",
    )
    db.add(new_case)
    db.commit()

    # 3. Read it back
    saved_case = db.query(CaseModel).filter(CaseModel.case_id == "CASE-1001").first()
    assert saved_case is not None
    assert saved_case.suspected_drug == "Amoxicillin"
    assert saved_case.status == "submitted"

    # 4. Clean up
    db.delete(saved_case)
    db.commit()
    db.close()

