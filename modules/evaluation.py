def evaluate_keywords(predicted_keywords, gold_keywords):
    # Token-level comparison: flatten phrases into individual words
    predicted_tokens = set()
    for kw in predicted_keywords:
        predicted_tokens.update(kw.lower().strip().split())

    gold_tokens = set()
    for kw in gold_keywords:
        gold_tokens.update(kw.lower().strip().split())

    true_positives = len(predicted_tokens & gold_tokens)
    false_positives = len(predicted_tokens - gold_tokens)
    false_negatives = len(gold_tokens - predicted_tokens)

    precision = true_positives / (true_positives + false_positives) if predicted_tokens else 0.0
    recall = true_positives / (true_positives + false_negatives) if gold_tokens else 0.0
    f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "precision": precision,
        "recall": recall,
        "f1_score": f1_score
    }
