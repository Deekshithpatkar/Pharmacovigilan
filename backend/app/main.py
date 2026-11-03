from fastapi import FastAPI
from app.api.routes import health

app = FastAPI(
    title="Pharmacovigilance API",
    description="Adverse-event reporting and triage system",
    version="0.1.0",
)

app.include_router(health.router)

@app.get("/")
def root():
    return {"message": "Pharmacovigilance API is running"}
