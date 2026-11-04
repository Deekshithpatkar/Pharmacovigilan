from fastapi import FastAPI
from app.database import engine, Base
from app.api.routes import health, cases

# Ensure database tables exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Pharmacovigilance API",
    description="Adverse-event reporting and triage system",
    version="0.1.0",
)

app.include_router(health.router)
app.include_router(cases.router)

@app.get("/")
def root():
    return {"message": "Pharmacovigilance API is running"}
