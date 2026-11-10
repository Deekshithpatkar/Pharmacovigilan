# Deterministic Triage & Safety Rules

To avoid non-deterministic or hallucinated clinical decisions, all safety classifications follow strict deterministic triage rules:

## Rule 1 — URGENT (Immediate Escalation)
- **Condition:** Clinical Severity $\ge 4$ OR report contains life-threatening keywords (`death`, `fatal`, `anaphylaxis`, `cardiac arrest`, `seizure`, `respiratory arrest`, `organ failure`, `coma`).
- **Action:** Mark priority as `URGENT`, route to `human_review`, and alert the medical safety officer.

## Rule 2 — REVIEW REQUIRED (Potential New Safety Signal)
- **Condition:** The reported reaction is **not listed** in the official drug label passages (`is_listed: false`) OR drug label evidence could not be retrieved.
- **Action:** Mark priority as `REVIEW_REQUIRED`, route to `human_review` to investigate potential unexpected adverse events.

## Rule 3 — ROUTINE (Standard Surveillance)
- **Condition:** Reaction is confirmed listed in the drug label AND severity $\le 3$ AND no duplicate conflict.
- **Action:** Mark priority as `ROUTINE`, complete the case automatically (`status: completed`), and persist in the safety database for aggregate signal detection.
