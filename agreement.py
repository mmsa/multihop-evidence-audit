"""Summarise independent reader agreement before adjudication."""
import argparse
from collections import Counter
from analyse import load
from pathlib import Path

def labels(path):
    rows = load(path)
    values = {r["item"]: r["verdict"].strip() for r in rows}
    if not values or len(values) != len(rows) or not set(values.values()) <= {
        "single", "joint", "insufficient", "indeterminate"
    }:
        raise ValueError("Each review item needs one complete verdict")
    return values

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("reader_a", type=Path)
    parser.add_argument("reader_b", type=Path)
    args = parser.parse_args()
    a, b = labels(args.reader_a), labels(args.reader_b)
    if a.keys() != b.keys():
        raise ValueError("Review packets cover different items")
    n = len(a)
    ca, cb = Counter(a.values()), Counter(b.values())
    observed = sum(a[i] == b[i] for i in a) / n
    chance = sum(ca[k] * cb[k] for k in ca) / n**2
    print("items:", n, "agreement:", observed)
    print("Cohen kappa:", (observed-chance)/(1-chance) if chance < 1 else "undefined")
    print("items requiring adjudication:", sorted(i for i in a if a[i] != b[i]))

if __name__ == "__main__":
    main()
