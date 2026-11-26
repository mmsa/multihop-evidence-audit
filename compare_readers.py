"""Compare two independently completed TSVs against the retrieval scoring key."""
import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

from analyse import interval, load

LABELS = {"single", "joint", "insufficient", "indeterminate"}
POSITIVE = {"single", "joint"}
METHODS = ("BM25", "BGE", "BGE-title-link")

def read_labels(path, expected):
    with path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    labels = {r["item"]: r["verdict"].strip() for r in rows}
    if len(rows) != len(expected) or labels.keys() != expected or not set(labels.values()) <= LABELS:
        raise ValueError(f"Incomplete, duplicate, unexpected or invalid labels in {path}")
    for r in rows:
        if not r["reason"].strip() or (r["verdict"] in POSITIVE and not r["evidence_quotes"].strip()):
            raise ValueError(f"Missing explanation or positive evidence in {path}: {r['item']}")
    return labels

def agreement(a, b):
    counts = Counter(zip(a, b))
    n = len(a)
    matches = sum(x == y for x, y in zip(a, b))
    first, second = Counter(a), Counter(b)
    chance = sum(first[x] * second[x] for x in first) / n**2
    return {"matched": matches, "total": n, "fraction": matches/n,
            "kappa": (matches/n - chance)/(1-chance) if chance < 1 else None,
            "cross_tab": {f"{x}/{y}": v for (x,y), v in sorted(counts.items())}}

def compare(predictions, paths):
    questions = defaultdict(dict)
    expected = {r["item"] for r in predictions}
    for r in predictions:
        questions[r["question_id"]][r["method"]] = r
    if len(predictions) != len(METHODS)*len(questions) or any(set(q)!=set(METHODS) for q in questions.values()):
        raise ValueError("Expected a single prediction per question and method")
    readers = [read_labels(path, expected) for path in paths]
    items = sorted(expected)
    values = [[reader[i] for i in items] for reader in readers]
    out = {"questions":len(questions), "sets":len(items), "four_way":agreement(*values),
           "binary":agreement(*[[v in POSITIVE for v in vs] for vs in values]),
           "disagreements":[i for i in items if readers[0][i]!=readers[1][i]],
           "readers":{}}
    for name, reader in zip(("A","B"),readers):
        methods = {}
        for m in METHODS:
            rows = [q[m] for q in questions.values()]
            methods[m] = {"gold":sum(int(r["gold"]) for r in rows),
                          "sufficient":sum(reader[r["item"]] in POSITIVE for r in rows),
                          "labels":dict(Counter(reader[r["item"]] for r in rows)),
                          "newly_credited":dict(Counter(reader[r["item"]] for r in rows
                                              if r["gold"]=="0" and reader[r["item"]] in POSITIVE)),
                          "gold_rejected":sum(r["gold"]=="1" and reader[r["item"]] not in POSITIVE for r in rows)}
        out["readers"][name]={"methods":methods,"contrasts":{}}
        for a,b in [(METHODS[1],METHODS[0]),(METHODS[2],METHODS[1])]:
            diffs,changes=[],[]
            for q in questions.values():
                x,y=q[a],q[b]
                d=int(reader[x["item"]] in POSITIVE)-int(reader[y["item"]] in POSITIVE)
                diffs.append(d)
                changes.append(d-(int(x["gold"])-int(y["gold"])))
            out["readers"][name]["contrasts"][f"{a} minus {b}"]={"gap":interval(diffs),"gap_change":interval(changes)}
    # Sharp bounds allowing each disputed item either reader's binary decision.
    # Identical question/passage outputs have one decision shared by both methods.
    out["dispute_bounds_counts"]={}
    for a,b in [(METHODS[1],METHODS[0]),(METHODS[2],METHODS[1])]:
        low,high=0,0
        for q in questions.values():
            i,j=q[a]["item"],q[b]["item"]
            if i!=j:
                x=[int(r[i] in POSITIVE) for r in readers]
                y=[int(r[j] in POSITIVE) for r in readers]
                low+=min(x)-max(y)
                high+=max(x)-min(y)
        out["dispute_bounds_counts"][f"{a} minus {b}"]=[low,high]
    return out

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("predictions",type=Path)
    parser.add_argument("reader_a",type=Path)
    parser.add_argument("reader_b",type=Path)
    args=parser.parse_args()
    print(json.dumps(compare(load(args.predictions),[args.reader_a,args.reader_b]),indent=2))
