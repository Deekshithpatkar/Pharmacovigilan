# Stage 3: Operational Pharmacovigilance Readiness & Regulatory Governance

This document establishes the operational standards, data privacy controls, security practices, and standard operating procedures (SOPs) required before evaluating the pharmacovigilance system for real-world hospital or pharmaceutical deployment.

---

## 1. Regulatory Governance & Standards Compliance

To operate in regulated environments, the system aligns with international regulatory frameworks:

- **FDA 21 CFR Part 314.80 / 312.32 (Postmarketing & IND Reporting):**
  - Serious adverse events (death, life-threatening, in-patient hospitalization) must be flagged within 15 calendar days (7 days for fatal/unexpected events).
- **FDA 21 CFR Part 11 (Electronic Records & Electronic Signatures):**
  - Requires computer-generated, time-stamped, immutable audit trails tracking all case alterations.
- **ICH E2B(R3) & ICH E2D Standards:**
  - Standardized electronic transmission format for Individual Case Safety Reports (ICSRs).
- **GAMP 5 (Good Automated Manufacturing Practice):**
  - Structured computerized system validation and change-control lifecycle.

---

## 2. Security, Authentication & Role-Based Access Control (RBAC)

In operational deployment, endpoints must not be publicly open without role boundaries:

| Role | Permissions |
|---|---|
| **Public Reporter / Patient** | Submit reports (`POST /cases`), lookup own case status by Case ID. |
| **Nurse / Clinical Staff** | Submit clinical reports with structured medical history, view ward cases. |
| **Safety Officer / Reviewer** | Access Reviewer Queue (`/review/pending`), adjudicate cases, add clinical notes. |
| **System Admin / Compliance Officer** | View immutable audit trails (`/cases/{id}/audit`), manage user access and API keys. |

### Technical Controls:
1. **Zero Secret Leakage:** Environment variables and API keys must be loaded exclusively via `.env` (guarded by `.gitignore`) and stored in vault management services (e.g., AWS Secrets Manager, HashiCorp Vault) in cloud environments.
2. **Data-at-Rest Encryption:** AES-256 encryption on PostgreSQL storage and backup snapshots.
3. **Data-in-Transit Encryption:** TLS 1.3 encryption across all API and Streamlit communications.

---

## 3. Patient Privacy & HIPAA / GDPR Compliance

Adverse drug event narratives often contain sensitive Protected Health Information (PHI):

1. **De-Identification & Redaction:**
   - Patient names, addresses, phone numbers, and Social Security numbers are scrubbed or excluded at ingestion.
   - Reports are keyed by pseudonymous identifiers (e.g., `PV-A1B2C3D4`).
2. **Data Retention & Archival Policies:**
   - Safety records must be retained in accordance with pharmacovigilance statutes (typically 10–25 years post drug lifecycle).
   - Backup snapshots are stored in write-once-read-many (WORM) storage.

---

## 4. Standard Operating Procedures (SOPs)

### SOP-PV-001: Intake & Triage Protocol
1. New reports must undergo duplicate verification within 2 hours of arrival.
2. High-severity (`URGENT`) cases trigger automated email/webhook notifications to on-call medical safety specialists.

### SOP-PV-002: Clinical Adjudication
1. Reviewers must confirm drug exposure, check concurrent medications, and record an explicit rationale in reviewer notes.
2. A case cannot be marked `COMPLETED` without recording the reviewer identity and timestamp in the audit trail.

### SOP-PV-003: Signal Detection & Regulatory Submission
1. Routine and adjudicated cases are pooled monthly for Disproportionality Analysis (PRR / ROR metrics).
2. Identified safety signals are escalated to the Pharmacovigilance Risk Assessment Committee (PRAC).

---

## 5. Scope Boundary & Legal Disclaimer
> **Clinical & Legal Disclaimer:** This software is an automated decision-support prototype. It is not an FDA-cleared medical device and does not establish independent clinical diagnoses or replace qualified clinical judgement. Operational deployment requires formal institutional review board (IRB) approval, institutional IT sign-off, and organizational validation.

