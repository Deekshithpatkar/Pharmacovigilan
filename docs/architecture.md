# System Architecture

## Overview
The Pharmacovigilance System is an end-to-end decision-support pipeline designed to intake, validate, extract, verify, and triage adverse drug reaction reports.

```text
[ Patient / Reporter ]
         │ (Streamlit Web UI / REST API)
         ▼
[ Report Validation & Ingestion ] ──> [ Duplicate Case Detection ]
         │
         ▼
[ AI Information Extraction (Gemini / MedDRA) ]
         │
         ▼
[ Drug-Label Evidence Retrieval (openFDA / Local RAG) ]
         │
         ▼
[ Evidence Verification & Deterministic Safety Triage ]
         ├── Severe or Unlisted Reaction ──> [ Human Reviewer Queue ] ──> [ Safety Officer Adjudication ]
         └── Mild, Listed Reaction ─────────> [ Automated Routine Storage ]
         │
         ▼
[ Immutable Audit Trail & Database Persistence (PostgreSQL) ]
```

## Key Technical Components
- **API & Core:** FastAPI, Pydantic, SQLAlchemy 2.0, Alembic, PostgreSQL / SQLite
- **AI Extraction & Normalization:** Gemini Structured Outputs, MedDRA standardized terms
- **Label Retrieval (RAG):** openFDA REST API and versioned JSON drug labels
- **Safety Triage:** Deterministic rules enforcing 100% serious event sensitivity
- **Audit & Governance:** Immutable event log tracking every status transition
- **User Interface:** Streamlit multi-page web application
