# Development Benchmark Dataset

This benchmark dataset contains labeled reference cases used to evaluate:
1. **Extraction Accuracy**: Precision and Recall for suspected drug names and reaction terms.
2. **Safety Triage Performance**: Sensitivity for severe/urgent cases (ensuring no life-threatening reaction is missed).
3. **Routing Correctness**: Whether human review was properly recommended.

Each test case contains:
- `id`: Unique identifier
- `text`: Free-text adverse event description
- `expected_drug`: Expected normalized drug name
- `expected_reactions`: Ground-truth reaction terms
- `expected_priority`: Target triage priority (`URGENT`, `REVIEW_REQUIRED`, `ROUTINE`)
- `is_serious`: Ground-truth clinical seriousness

