# Blinded AI evidence review

Two AI agents reviewed each of 303 pooled outputs in separate, fresh sessions. Both used the same assistant configuration and rubric. Each received a separately shuffled packet containing item identifiers, questions, proposed answers, two titles and their passages. Their task excluded system names, reference passage labels, the manuscript, external lookup and the other agent's decisions. They recorded a verdict, supporting text for positive decisions and a reason. These are AI-generated annotations. Human validation remains open.

The four verdicts are defined in [REVIEW.md](../REVIEW.md). The primary binary outcome credits single and joint support. Each retrieval method receives the label assigned to its own passage set. Repeated outputs for the same question share a label. Do not pool the two readers as if they supplied independent question samples. Summary intervals resample questions within one dataset and hold the reader's labels fixed. The dispute bounds choose either observed binary label for each disputed set while respecting shared outputs. These are sensitivity bounds within the pilot.

Each dataset directory contains the original reader TSVs and a machine-readable summary. The four-way cross-tabulation uses A/B order. Keys in newly_credited distinguish single-passage shortcuts from cases in which the reader needed both passages. gold_rejected counts annotated pairs rated insufficient or indeterminate. Short quoted excerpts retain the attribution and licensing of the underlying material.

Reproduce from the repository root:

    python compare_readers.py results/predictions.csv reviews/hotpotqa/reader_a.tsv reviews/hotpotqa/reader_b.tsv
    python compare_readers.py musique-results/predictions.csv reviews/musique/reader_a.tsv reviews/musique/reader_b.tsv

## AI peer-review comments after annotation
Reviewer A identified passage sufficiency versus gold recovery as the main contribution and recommended a human audit covering AI agreements as well as disputes. Reviewer B identified question–answer mismatches as a potential source of low sufficiency scores and recommended a sensitivity analysis. The revised paper includes a narrow post hoc year-answer check. These comments followed completion of the reviewers’ labels.
