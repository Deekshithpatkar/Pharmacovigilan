from typing import List, Set

def compute_precision_recall_f1(predicted: List[str], expected: List[str]):
    """Calculate Precision, Recall, and F1 score for extracted terms."""
    pred_set: Set[str] = set(p.lower().strip() for p in predicted)
    exp_set: Set[str] = set(e.lower().strip() for e in expected)

    if not pred_set and not exp_set:
        return 1.0, 1.0, 1.0
    if not pred_set or not exp_set:
        return 0.0, 0.0, 0.0

    true_positives = len(pred_set.intersection(exp_set))
    precision = true_positives / len(pred_set) if pred_set else 0.0
    recall = true_positives / len(exp_set) if exp_set else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return precision, recall, f1

def compute_serious_sensitivity(serious_detected: int, total_serious: int) -> float:
    """Calculate sensitivity for serious/urgent cases (True Positive Rate)."""
    if total_serious == 0:
        return 1.0
    return serious_detected / total_serious

