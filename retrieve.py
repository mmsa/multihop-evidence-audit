"""Retrieve paired paragraphs, pool identical sets and create blinded review packets."""
import argparse
import csv
import hashlib
import json
import math
import random
import re
from collections import Counter
from itertools import combinations
from pathlib import Path

import torch
from transformers import BertModel, PreTrainedTokenizerFast

def terms(text):
    return re.findall(r"\w+", text.casefold())

def bm25(query, passages):
    counts = [Counter(terms(p)) for p in passages]
    lengths = [sum(c.values()) for c in counts]
    avg = sum(lengths) / len(lengths)
    scores = [0.0] * len(counts)
    for term in sorted(set(terms(query))):
        df = sum(term in c for c in counts)
        idf = math.log1p((len(counts) - df + 0.5) / (df + 0.5))
        for i, c in enumerate(counts):
            tf = c[term]
            scores[i] += idf * tf * 2.2 / (tf + 1.2 * (0.25 + 0.75 * lengths[i] / avg))
    return scores

def top_two(scores):
    return tuple(sorted(sorted(range(len(scores)), key=lambda i: (-scores[i], i))[:2]))

def title_link(titles, bodies, scores):
    norm = [" " + " ".join(terms(body)) + " " for body in bodies]
    keys = [" " + " ".join(terms(title)) + " " for title in titles]
    def score(pair):
        a, b = pair
        linked = keys[a] in norm[b] or keys[b] in norm[a]
        return scores[a] + scores[b] + 0.05 * linked
    return max(combinations(range(len(scores)), 2), key=score)

def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

def main():
    parser = argparse.ArgumentParser()
    for name in ("sample", "model", "output"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    if args.output.exists() and any(args.output.iterdir()):
        parser.error("Choose an empty output directory to preserve existing reviews.")
    torch.set_num_threads(4)
    model = BertModel.from_pretrained(args.model, local_files_only=True).eval()
    tokenizer = PreTrainedTokenizerFast(tokenizer_file=str(args.model / "tokenizer.json"),
                                        pad_token="[PAD]", unk_token="[UNK]")
    reviews, predictions, items = [], [], []
    with torch.inference_mode():
        for row in json.loads(args.sample.read_text()):
            titles = row["context"]["title"]
            bodies = [" ".join(s.strip() for s in sentences) for sentences in row["context"]["sentences"]]
            docs = [t + ". " + p for t, p in zip(titles, bodies)]
            query = row["question"]
            inputs = tokenizer(["Represent this sentence for searching relevant passages: " + query] + docs,
                               padding=True, truncation=True, max_length=512, return_tensors="pt")
            vectors = torch.nn.functional.normalize(model(**inputs).last_hidden_state[:, 0], dim=-1)
            scores = (vectors[1:] @ vectors[0]).tolist()
            systems = {"BM25": top_two(bm25(query, docs)), "BGE": top_two(scores),
                       "BGE-title-link": title_link(titles, bodies, scores)}
            gold = set(row["supporting_facts"]["title"])
            items.append({"id": row["id"], "type": row["type"], "gold_titles": sorted(gold)})
            for pair in sorted(set(systems.values())):
                indices = list(pair)
                item = hashlib.sha256((row["id"] + str(pair)).encode()).hexdigest()[:16]
                random.Random(item).shuffle(indices)
                a, b = indices
                reviews.append(dict(item=item, question=query, proposed_answer=row["answer"],
                                    title_a=titles[a], passage_a=bodies[a], title_b=titles[b], passage_b=bodies[b],
                                    verdict="", evidence_quotes="", reason=""))
                matches = (int(set(pair) == set(row["gold_indices"])) if "gold_indices" in row
                           else int({titles[a], titles[b]} == gold))
                for method, result in systems.items():
                    if result == pair:
                        predictions.append(dict(question_id=row["id"], method=method, item=item, gold=matches,
                                                title_a=titles[a], title_b=titles[b]))
    args.output.mkdir(parents=True, exist_ok=True)
    for name in ("reader_a", "reader_b"):
        order = list(reviews)
        random.Random(name).shuffle(order)
        write_csv(args.output / (name + ".csv"), order)
    write_csv(args.output / "predictions.csv", predictions)
    (args.output / "sample_ids.json").write_text(json.dumps(items, indent=2))
    print("questions, pooled sets:", len(items), len(reviews))

if __name__ == "__main__":
    main()
