# Multi-hop evidence audit
[Read the working paper (PDF)](Evidence-Audit.pdf) · [LaTeX source](paper.tex)

A reproducible pilot comparing annotated-title retrieval with blinded AI judgements of evidence sufficiency. Read paper.md for findings and limitations.

## Reproduction
Use Python 3.12 with the dependencies in requirements.txt. Supply a HotpotQA distractor validation Parquet file with the Hugging Face HotpotQA schema (https://huggingface.co/datasets/hotpotqa/hotpot_qa), and a local BGE-small English BERT checkpoint directory containing config.json, tokenizer.json and model.safetensors. Input fingerprints below identify the exact local files used.

    python sample.py hotpotqa-distractor-validation.parquet sample.json
    python retrieve.py sample.json /path/to/bge-model my-results
    python analyse.py my-results/predictions.csv

Retrieve into a fresh output directory to preserve filled worksheets. The included results/ files are the actual pilot run. CPU inference uses four threads. Scores use local candidate-pool BM25 with k1=1.2, b=0.75 and BGE query instruction, 512-token truncation. The exploratory title-link bonus was specified before this run. The original confidence-gated fact-slot retriever is absent from this comparison.

Input SHA-256 fingerprints:
- Development Parquet: c20b638ca82b21d04fe12e14ff417ad05153d4d215a65de54497fca4e972f7c6
- BGE weights: 3c9f31665447c8911517620762200d2245a2518d6e7208acc78cd9db317e21ad
- Tokenizer: d241a60d5e8f04cc1b2b3e9ef7a4921b27bf526d9f6050ab90f9267a1f9e5c66

## Independent review
Give each reader only REVIEW.md and their own CSV. Do not send the paper or the predictions, examples or key before they finish. Store their completed sheets separately. Reconcile disagreements together and save one adjudicated copy. Use the item ID to align rows, since the orders differ.

    python agreement.py completed_a.csv completed_b.csv
    python analyse.py results/predictions.csv --adjudicated final.csv

## Attribution
Python scripts are released under the MIT License. HotpotQA-derived CSVs and question metadata are adapted from Yang et al. and Wikipedia under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Transformations include deterministic sampling, selecting passages, joining sentences and shuffling rows. Passage titles accompany excerpts. [HotpotQA project and data](https://hotpotqa.github.io/).

## MuSiQue two-hop replication
Use the answerable development JSONL from [the authors](https://github.com/StonyBrookNLP/musique). The dataset is available under CC BY 4.0. MuSiQue-derived IDs, titles and scores in musique-results/ are from the 100-question sample. The input SHA-256 is 15fa63794d18a94ce12411aca6e2327e65b6e83b0b1490efab3f1962e48abf3b.

    python sample_musique.py musique_ans_v1.0_dev.jsonl musique.json
    python retrieve.py musique.json /path/to/bge-model my-musique-results
    python analyse.py my-musique-results/predictions.csv

| Annotated pair recovered | HotpotQA (50) | MuSiQue (100) |
|---|---:|---:|
| BM25 | 9 | 13 |
| BGE | 24 | 26 |
| BGE with title links | 29 | 27 |

The public results contain scoring keys. Generate the two shuffled reader worksheets with retrieve.py and distribute each sheet privately with REVIEW.md. Two AI readers completed the blinded audit. Their labels, disagreement counts and paired comparisons are available in [reviews/](reviews/). Independent human validation remains pending.
