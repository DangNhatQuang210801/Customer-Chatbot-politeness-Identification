import json, re, argparse
from pathlib import Path

DEFAULT_RULES = {
    "T01_EmpathyGratitude": r"\b(thank(?:s| you)|appreciate|i understand|we understand|we'?re here to help|happy to help)\b",
    "T02_Apology": r"\b(sorry|apolog(?:y|ize|ise|ized|ised|izing|ising)|apologies|regret)\b",
    "T03_PositiveFlex": r"\b(expedite|prioriti[sz]e|urgent|we'?ll (try|do our best)|i'?ll (try|do my best))\b",
    "T04_MitigationHedge": r"\b(might|may|could|usually|typically|generally|possibly|perhaps|unfortunately)\b",
    "T05_GuidancePolicy": r"\b(go to|open|select|click|choose|visit|navigate|tap|your orders|help center|policy|return within|terms|start a return|request a refund)\b",
    "T06_RefusalMinus": r"\b(can'?t|cannot|unable to|not possible|won'?t be able)\b",
}

def compile_rules(rule_dict):
    return {k: re.compile(v, re.I) for k, v in rule_dict.items()}

def predict_labels(text, patterns):
    t = (text or "").lower()
    labels = [tag for tag, pat in patterns.items() if pat.search(t)]
    if not labels:
        labels = ["skip/unclear"]
    return labels

def build_predictions(tasks, model_version="rules-v3-multilabel", rules=None):
    pats = compile_rules(rules or DEFAULT_RULES)
    preds = []
    for item in tasks:
        task_id = item.get("id")
        text = item.get("data", {}).get("reply_text", "")
        labels = predict_labels(text, pats)
        preds.append({
            "task": task_id,
            "model_version": model_version,
            "score": 0.5,
            "result": [{
                "from_name": "label",
                "to_name": "reply_text",
                "type": "choices",
                "value": {"choices": labels}
            }]
        })
    return preds

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", required=True, help="Path to tasks_clean.json (Label Studio tasks)")
    ap.add_argument("--out", required=True, help="Path to write predictions JSON (flat format for Settings→Predictions)")
    ap.add_argument("--model", default="rules-v3-multilabel", help="Model version string")
    ap.add_argument("--rules", default="", help="Optional path to a JSON file with custom regex rules")
    args = ap.parse_args()

    with open(args.tasks, "r", encoding="utf-8") as f:
        tasks = json.load(f)

    rules = None
    if args.rules:
        with open(args.rules, "r", encoding="utf-8") as f:
            rules = json.load(f)

    predictions = build_predictions(tasks, model_version=args.model, rules=rules)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(predictions, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(predictions)} predictions to {args.out}")

if __name__ == "__main__":
    main()
