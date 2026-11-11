# Pharmacovigilance System

## 1. Project Goal

Build a pharmacovigilance case-processing and triage system that accepts adverse-event reports from patients, nurses, doctors, pharmacists, and other reporters through a web interface.

The system will validate reports, create and store cases, check for possible duplicates, extract structured information using an LLM, retrieve relevant drug-label evidence, apply safety triage rules, and route urgent or uncertain cases for human review.

The project will be built in stages so it can first serve as a portfolio/research prototype and later be evaluated for possible use in a hospital or pharmaceutical-company setting.

**Important scope boundary:** this project is a decision-support prototype. It must not present AI outputs as confirmed medical conclusions or replace qualified medical review. Building the software does not, by itself, establish clinical validation or regulatory readiness.

## 2. End-to-End Workflow

1. **Report submission**
   - A reporter enters an adverse-event description and available case details through the website.
2. **Validation and case creation**
   - Check required fields and data formats.
   - If required information is missing or invalid, ask the reporter to correct it.
   - Assign a case ID and store the report.
3. **Duplicate check**
   - Search for similar existing cases.
   - If a possible duplicate is found, link it for reviewer assessment rather than silently discarding it.
4. **AI information extraction**
   - Extract available drug names, reactions/symptoms, onset date, outcome, and severity information.
   - Normalize drug names and map reaction terms to standardized terminology where appropriately licensed.
5. **Drug-label evidence retrieval (RAG)**
   - Retrieve relevant drug-label passages.
   - Preserve source references, including label/version and section details when available.
6. **Safety and triage assessment**
   - Check whether the reported reaction is described in the retrieved label evidence.
   - Apply documented deterministic triage rules.
   - Treat missing evidence as uncertainty; absence from retrieved passages does not prove that a reaction is unknown.
7. **Human review**
   - Route urgent, incomplete, conflicting, or uncertain cases for qualified human review.
   - A reviewer can confirm or update the triage and next action.
8. **Final case update and output**
   - Store the outcome, supporting evidence, decision trace, reviewer actions, and case status.
   - Display the preliminary result and follow-up status through the website.

## 3. Project Stages

### Stage 1 — Validated Case-Processing Prototype

Build the core software and its technical tests.

- Define a structured adverse-event case schema.
- Build the report-submission interface and FastAPI endpoint.
- Add mandatory-field and format validation.
- Create and persist case records in PostgreSQL.
- Add possible-duplicate detection.
- Add LLM-based structured information extraction.
- Normalize drug names and support standardized reaction terminology where appropriately licensed.
- Retrieve versioned drug-label evidence and preserve exact source references.
- Implement deterministic triage rules and human-review routing.
- Store case outcomes and decision/audit history.
- Add automated tests and a component-level evaluation harness.

**Stage 1 deliverable:** a working case-processing and triage prototype with traceable evidence and repeatable technical evaluation. This stage does not establish clinical validity.

### Stage 2 — Clinical Evaluation

Evaluate the prototype against appropriate reference cases and qualified review.

- Obtain de-identified cases and expert annotations through a qualified clinical or pharmacovigilance collaborator.
- Establish documented reference decisions and adjudicate disagreements.
- Define evaluation metrics and acceptance criteria before the final evaluation.
- Keep development data separate from the independent test set.
- Measure extraction quality, retrieval quality, evidence grounding, serious-event sensitivity, false negatives, routing performance, and subgroup performance where data permits.
- Run the system in shadow mode and document discrepancies without allowing its output to control patient care.
- Analyze errors, improve the system, and re-evaluate using a controlled process.

**Stage 2 deliverable:** a reproducible evaluation report with limitations, uncertainty, and documented findings. Synthetic cases can support development but cannot establish real-world clinical performance.

### Stage 3 — Operational Pharmacovigilance Readiness

Prepare the system for formal organizational review and possible real-world deployment.

- Add authentication and role-based access control.
- Implement appropriate encryption, secure configuration, backups, and data-retention controls.
- Maintain audit logs and traceable version history for models, prompts, rules, and label sources.
- Establish standard operating procedures, quality assurance, change control, and incident handling.
- Support appropriate case-report exports and regulatory workflows.
- Add aggregate safety-pattern analysis and signal-investigation support.
- Assess applicable clinical, quality, privacy, security, and regulatory requirements before deployment.

**Stage 3 deliverable:** an operationally hardened system prepared for formal review. Completing these tasks does not automatically mean the product is clinically validated or regulator-approved.

## 4. Technical Stack

- **Language:** Python
- **Backend API:** FastAPI
- **Validation and schemas:** Pydantic
- **Database:** PostgreSQL
- **Database ORM:** SQLAlchemy
- **Migrations:** Alembic
- **AI extraction:** an LLM that supports structured outputs
- **Retrieval:** embeddings and ChromaDB for drug-label passages
- **Workflow:** begin with ordinary Python orchestration; use LangGraph for conditional workflow routing when needed
- **Frontend:** Streamlit for the initial interface
- **Testing:** Pytest
- **Evaluation:** Python metrics and reproducible benchmark scripts
- **Deployment/local services:** Docker Compose when needed

## 5. Planned Folder Structure

```text
pharmacovigilance-system/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── dependencies.py
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── cases.py
│   │   │   │   ├── health.py
│   │   │   │   └── review.py
│   │   │   └── schemas/
│   │   │       ├── case.py
│   │   │       └── response.py
│   │   ├── models/
│   │   │   ├── case.py
│   │   │   ├── drug.py
│   │   │   └── audit_log.py
│   │   ├── services/
│   │   │   ├── case_service.py
│   │   │   ├── validation_service.py
│   │   │   ├── duplicate_service.py
│   │   │   └── review_service.py
│   │   ├── ai/
│   │   │   ├── extraction.py
│   │   │   ├── normalization.py
│   │   │   ├── label_retrieval.py
│   │   │   ├── evidence_verification.py
│   │   │   └── triage.py
│   │   ├── workflows/
│   │   │   └── case_workflow.py
│   │   └── utils/
│   │       └── logging.py
│   ├── migrations/
│   ├── tests/
│   │   ├── test_cases.py
│   │   ├── test_validation.py
│   │   ├── test_duplicates.py
│   │   └── test_triage.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── app.py
│   ├── pages/
│   │   ├── submit_report.py
│   │   ├── case_status.py
│   │   └── reviewer_dashboard.py
│   └── components/
│       ├── report_form.py
│       └── evidence_viewer.py
├── evaluation/
│   ├── datasets/
│   │   └── README.md
│   ├── benchmarks/
│   ├── metrics.py
│   ├── run_evaluation.py
│   └── reports/
├── data/
│   ├── drug_labels/
│   └── chroma_db/
├── docs/
│   ├── architecture.md
│   ├── case_schema.md
│   └── triage_rules.md
├── scripts/
│   └── seed_database.py
├── .gitignore
├── README.md
└── docker-compose.yml
```

Create files when their corresponding stage is implemented; the structure is the planned organization, not a requirement to implement every module at once. Local data stores and secrets must be excluded from version control. Commit `.env.example`, never real credentials.

## 6. Evaluation Plan

Evaluation is part of development from the beginning.

| Component | Measurements |
|---|---|
| Case validation | Required-field and format-validation tests |
| Duplicate detection | Precision/recall on labelled duplicate examples when available |
| Information extraction | Precision, recall, and F1 for extracted fields |
| Drug-label retrieval | Recall@k and relevance of retrieved passages |
| Evidence grounding | Citation correctness, quote verification, unsupported-claim rate |
| Serious-event routing | Sensitivity, false-negative rate, specificity, and PPV where reference labels permit |
| End-to-end workflow | Agreement with reference decisions, escalation performance, and failure analysis |
| Robustness | Missing fields, ambiguous reports, multiple drugs, conflicting evidence, and API failures |
| Operations | Latency, failure rate, data integrity, and audit completeness |

Set acceptance criteria before independent testing, report confidence intervals where appropriate, and document limitations. Do not use the development dataset as the final independent test set. Serious-event misses require particular attention; overall accuracy alone is insufficient.

## 7. Implementation Order

Follow this order and keep it stable unless a documented technical dependency requires a change.

1. Create the repository and planned folder structure.
2. Define the case schema and request/response schemas.
3. Set up PostgreSQL, SQLAlchemy, and database migrations.
4. Build the FastAPI application and health endpoint.
5. Implement report submission, mandatory-field validation, case IDs, and database persistence.
6. Add duplicate detection and reviewer linking.
7. Add LLM-based information extraction and validate its structured output.
8. Add drug-name normalization and standardized reaction terminology where appropriately licensed.
9. Add drug-label ingestion/retrieval, label versioning, and source references.
10. Add evidence verification and deterministic triage rules.
11. Add conditional workflow orchestration and human-review routing.
12. Build the Streamlit report form, case-status view, and reviewer dashboard.
13. Add audit history and case-status updates.
14. Write and run component and integration tests.
15. Create a development benchmark and evaluation reports.
16. Proceed to Stage 2 only when the Stage 1 prototype and its tec
hnical evaluation are documented.
17. Proceed to Stage 3 only after the clinical evaluation plan, findings, risks, and applicable requirements have been reviewed.

## 8. Safety and Scope Rules

- The system supports review; it does not diagnose a patient or establish causality by itself.
- Do not equate “not found in retrieved label passages” with “unknown adverse reaction.”
- Seriousness, severity, causality, expectedness, and urgency are distinct concepts and must not be treated as interchangeable.
- Route urgent or uncertain cases to qualified human review according to documented rules.
- Preserve the evidence, rule version, model/prompt version, and review history used for each result.
- Use synthetic data during early development. Use real case data only with appropriate authorization, de-identification, access controls, and governance.
- Do not claim clinical validation, regulatory compliance, or approval without the corresponding evidence and required review.

## 9. Definition of Done for Phase 1

Phase 1 is complete when:

- A reporter can submit a case through the web interface.
- Required fields and formats are validated.
- Each accepted report receives a case ID and is stored in PostgreSQL.
- Possible duplicates are identified and linked for review.
- The AI extracts structured information with schema validation.
- Drug-label evidence is retrieved with traceable source references.
- Triage rules produce a documented preliminary outcome and route uncertain or urgent cases for human review.
- Case status, evidence, and decision history are persisted and viewable.
- Automated tests and a repeatable component-level evaluation have been run.
- Known limitations and evaluation results are documented.

**The immediate next task is Step 1: create the repository and folder structure, then implement the case schema and database foundation.**
