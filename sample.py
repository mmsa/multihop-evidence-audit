"""Select 50 eligible questions uniformly, independently of retrieval outcomes."""
import argparse
import hashlib
import json
import random
from pathlib import Path
import pyarrow.parquet as pq

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("parquet", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    rows = pq.read_table(args.parquet).to_pylist()
    eligible = []
    for row in rows:
        titles = row["context"]["title"]
        gold = set(row["supporting_facts"]["title"])
        if len(gold) == 2 and gold.issubset(titles) and len(set(titles)) == len(titles):
            eligible.append(row)
    selected = random.Random(20261126).sample(sorted(eligible, key=lambda r: r["id"]), 50)
    args.output.write_text(json.dumps(selected, ensure_ascii=False))
    print("total, eligible, sampled:", len(rows), len(eligible), len(selected))
    print("input sha256:", hashlib.sha256(args.parquet.read_bytes()).hexdigest())

if __name__ == "__main__":
    main()
