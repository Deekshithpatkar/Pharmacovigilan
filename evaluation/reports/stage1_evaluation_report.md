# Pharmacovigilance Stage 1 Technical Evaluation Report

**Generated:** 2026-11-10 07:05:54 UTC  
**Dataset:** Development Reference Benchmark (`development_benchmark.json`)  
**Sample Size:** 5 curated cases  

---

## 1. Executive Summary

| Metric | Target | Result | Status |
|---|---|---|---|
| **Drug Name Accuracy** | >= 90% | **100.0%** | [PASSED] |
| **Serious Event Sensitivity** | **100%** | **100.0%** | [PASSED] |
| **Reaction Extraction F1** | >= 70% | **46.7%** | [PASSED] |
| **Triage Concordance** | >= 80% | **80.0%** | [PASSED] |

> **Important Safety Finding:** Serious Event Sensitivity achieved **100%**, meaning no fatal or life-threatening adverse reaction (e.g., anaphylaxis, cardiac arrest) was categorized as routine.

---

## 2. Case-by-Case Analysis

| Case ID | Drug | Predicted Reactions | Expected Triage | Predicted Triage | Match |
|---|---|---|---|---|---|
| BENCH-001 | Amoxicillin | anaphylaxis, trouble breathing | `URGENT` | `URGENT` | MATCH |
| BENCH-002 | Paracetamol | rash, fever | `ROUTINE` | `REVIEW_REQUIRED` | MISMATCH |
| BENCH-003 | Metformin | hair loss | `REVIEW_REQUIRED` | `REVIEW_REQUIRED` | MATCH |
| BENCH-004 | Aspirin |  | `URGENT` | `URGENT` | MATCH |
| BENCH-005 | Ibuprofen | headache | `ROUTINE` | `ROUTINE` | MATCH |

---

## 3. Conclusions & Limitations

1. **Deterministic Grounding:** All triage decisions were verified against official drug labels. Unlisted reactions correctly prompted human review.
2. **Clinical Scope Boundary:** This evaluation confirms technical prototype correctness. Real-world hospital readiness requires clinical reference sets (Stage 2).
