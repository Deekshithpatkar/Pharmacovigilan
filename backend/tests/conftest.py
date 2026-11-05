import pytest
from app.database import engine, Base, SessionLocal
from app.models.case import CaseModel

@pytest.fixture(autouse=True)
def clean_db():
    """Ensure database has fresh tables and no leftover rows from previous tests."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    db.query(CaseModel).delete()
    db.commit()
    db.close()
    yield
    db = SessionLocal()
    db.query(CaseModel).delete()
    db.commit()
    db.close()
