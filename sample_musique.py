"""Sample the MuSiQue two-hop development stratum and retain passage indices."""
import argparse
import hashlib
import json
import random
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("jsonl", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    rows = [json.loads(line) for line in args.jsonl.read_text().splitlines()]
    eligible = [r for r in rows if r["answerable"] and len(r["question_decomposition"]) == 2
                and sum(p["is_supporting"] for p in r["paragraphs"]) == 2]
    selected = random.Random(20261127).sample(sorted(eligible, key=lambda r: r["id"]), 100)
    formatted = []
    for row in selected:
        paragraphs = row["paragraphs"]
        indices = [i for i,p in enumerate(paragraphs) if p["is_supporting"]]
        titles = [p["title"] for p in paragraphs]
        formatted.append(dict(id=row["id"], question=row["question"], answer=row["answer"], type="two-hop",
                              context=dict(title=titles, sentences=[[p["paragraph_text"]] for p in paragraphs]),
                              gold_indices=indices, supporting_facts=dict(title=[titles[i] for i in indices])))
    args.output.write_text(json.dumps(formatted, ensure_ascii=False))
    print(len(rows), len(eligible), len(selected), hashlib.sha256(args.jsonl.read_bytes()).hexdigest())

if __name__ == "__main__":
    main()
