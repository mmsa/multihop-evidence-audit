"""Question-paired analysis. Human labels are optional and must be complete."""
import argparse
import csv
import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean

def load(path):
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))

def interval(deltas):
    rng = random.Random(4401)
    samples = sorted(mean(rng.choices(deltas, k=len(deltas))) for _ in range(5000))
    return {"estimate": mean(deltas), "ci95": [samples[124], samples[4874]]}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("predictions", type=Path)
    parser.add_argument("--adjudicated", type=Path)
    args = parser.parse_args()
    rows = load(args.predictions)
    questions = defaultdict(dict)
    for r in rows:
        questions[r["question_id"]][r["method"]] = r
    methods = ["BM25", "BGE", "BGE-title-link"]
    if any(set(q) != set(methods) for q in questions.values()) or len(rows) != 3 * len(questions):
        raise ValueError("Incomplete or duplicate system runs")
    qrows = list(questions.values())
    out = {"n": len(qrows), "sets": len({r["item"] for r in rows}),
           "gold_counts": {m: sum(int(q[m]["gold"]) for q in qrows) for m in methods}}
    labels = {}
    if args.adjudicated:
        reviewed = load(args.adjudicated)
        expected = {r["item"] for r in rows}
        labels = {r["item"]: r["verdict"].strip() for r in reviewed}
        if len(reviewed) != len(expected) or set(labels) != expected or not all(
            v in {"single", "joint", "insufficient", "indeterminate"} for v in labels.values()
        ):
            raise ValueError("Expected one completed adjudicated verdict per pooled item")
        out["adjudicated_labels"] = dict(Counter(labels.values()))
    for a, b in [("BGE", "BM25"), ("BGE-title-link", "BGE")]:
        gold = [int(q[a]["gold"]) - int(q[b]["gold"]) for q in qrows]
        summary = {"different_sets": sum(q[a]["item"] != q[b]["item"] for q in qrows),
                   "gold_gap": interval(gold)}
        if labels:
            for name, accepted in [("sufficient", {"single", "joint"}), ("joint_only", {"joint"}),
                                   ("including_indeterminate", {"single", "joint", "indeterminate"})]:
                delta = [int(labels[q[a]["item"]] in accepted) - int(labels[q[b]["item"]] in accepted) for q in qrows]
                summary[name] = {"gap": interval(delta), "change_from_gold": interval(
                    [d - g for d, g in zip(delta, gold)])}
        out[a + " minus " + b] = summary
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()
