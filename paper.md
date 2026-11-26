# Does gold evidence change which retriever wins?
## A paired passage-retrieval audit on HotpotQA and MuSiQue
Mohamed Mostafa · Independent Researcher · 26 November 2026

### Abstract
A retriever can miss an annotated passage yet return enough information to establish an answer. Does this discrepancy change how we compare retrieval systems? We compared BM25, BGE and BGE with a fixed title-link bonus on 50 HotpotQA questions and 100 two-hop MuSiQue questions. Each system returned two passages from the supplied candidate pool. BGE recovered the annotated pair more often than BM25 on both datasets. Its advantage was 30 percentage points on HotpotQA (paired bootstrap 95% interval 14 to 46) and 13 points on MuSiQue (4 to 23). The exploratory title-link bonus gained five questions on HotpotQA and one on MuSiQue. Two blinded AI reviewers independently assessed 303 distinct passage sets. HotpotQA produced agreement on 102/105 binary sufficiency decisions. MuSiQue produced agreement on 197/198 binary sufficiency decisions. The BGE versus BM25 sufficiency gaps were 24 and 26 percentage points on HotpotQA and 14 and 15 on MuSiQue. These estimates describe AI judgements under a passage-only rubric. Human validation remains open.

### 1. Question and prior work
HotpotQA annotates supporting sentences for multi-document questions (Yang et al., 2018). Ni, Gardner and Dasigi (2021) identified false-negative contexts in multi-document QA and addressed them during training. Trivedi et al. (2020) studied disconnected reasoning, where apparently multi-hop tasks admit shortcuts. Our proposed contribution concerns evaluation: how much does a difference between two retrievers change when a reader judges the passages they actually returned? Answers supported by one passage and answers requiring an alternative chain have different implications and should be counted separately.

### 2. Methods
All 7,405 validation questions had two distinct supporting titles present in their candidate pool and unique candidate titles. Sorting by ID before seeded sampling gave 42 bridge and eight comparison questions. The same two-passage budget and supplied candidates were used for all systems. Neither answer text nor supporting annotations were inputs to retrieval. BM25 used per-question document frequencies over the supplied passages. BGE ranked title-plus-text by cosine similarity after normalized CLS pooling. An exploratory pair scorer added 0.05 to the sum of two BGE similarities when one passage body mentioned the other's normalized full title. This is a separate baseline from the previously studied confidence-gated system. Ties followed source order.

The automated outcome is exact recovery of the unordered pair of annotated paragraph titles. HotpotQA's official supporting-fact evaluation uses sentence-level annotations. For each contrast we resampled whole questions with replacement 5,000 times and calculated a percentile interval for the mean paired difference. The BGE versus BM25 contrast is primary. The title-link contrast is exploratory.

For a cross-dataset check we sampled 100 questions uniformly from the 1,252 answerable two-hop MuSiQue development questions with exactly two annotated supporting passages (Trivedi et al., 2022). The original split comprises 2,417 examples across hop counts. We held scoring, query instruction, passage budget and title bonus fixed. MuSiQue support was compared by passage index because two candidate paragraphs can share a title. We calculated all intervals within each dataset. Candidate pools and question construction differ, so raw scores across datasets do not isolate a dataset effect.

### 3. Pilot results
BM25 recovered the gold pair on 9/50 questions (18%), BGE on 24/50 (48%) and BGE with title links on 29/50 (58%). BGE alone succeeded on 19 questions where BM25 failed, and BM25 alone succeeded on four. Both recovered the pair on five and both missed it on 22. The title-link rule gained nine gold matches and lost four relative to BGE. Its net difference of 10 percentage points had a paired 95% interval from −4 to +24 points.

Across the three systems, 150 outputs reduced to 105 distinct question–passage sets. All three selected the same pair on six questions. A sufficient/insufficient decision on one of those six cannot change their relative scores. Keeping these questions in the denominator preserves the interpretation of each score as a rate over the sampled questions.

On MuSiQue, BM25 recovered both supporting passages for 13/100 questions, BGE for 26/100, and BGE with title links for 27/100. BGE and BM25 selected different pairs on 83 questions. The exploratory title rule changed the BGE selection on 17 questions but its net advantage was one point (95% interval −4 to +6). The direction of the BGE versus BM25 difference replicated. The two pilots give little basis for recommending the title-link bonus as a general improvement.

### 4. How many decisions would change the winner?
The gold-pair lead of BGE over BM25 amounts to 15 questions on HotpotQA and 13 on MuSiQue. If readers accept every annotated pair, BM25 would need 15 more newly credited answers than BGE to tie on HotpotQA, and 16 to overtake. The corresponding thresholds on MuSiQue are 13 and 14. A shared passage pair contributes zero to the paired gap however readers label it. If readers also reject some annotated pairs, the same arithmetic applies to the net correction (credits gained minus credits lost). These thresholds express how large a scoring change would be consequential; they are not estimates of how often valid alternatives occur.

### 5. What an exact miss can mean
One question asks for the alternative name of Shakespeare's comedy Twelfth Night. BM25 selected the play and the 1996 film adaptation. The passage about the play explicitly identifies the subtitle What You Will. The pair scores zero under exact annotated-title recovery. This is an illustrative single-passage shortcut. It supplies no evidence about the frequency of valid alternative two-hop chains.

Another question compares the ages of scientists Ernst Messerschmid and Philippe Perrin. BM25 retrieved Messerschmid and a French artist also named Philippe Perrin. Although the passages provide birth dates and include the proposed answer, the second passage describes the wrong person. Matching the answer string or finding two dates is insufficient. These illustrations were selected after inspecting system outputs and are excluded from any claim of independent human validation.

### 6. Blinded AI review
Two fresh AI agent sessions each assessed every pooled passage set. Each received a shuffled worksheet with the question, proposed answer and passages, including their titles. Both sessions used the same assistant configuration. Each worked without access to the system identities, annotated support, prior examples in the paper or the other session's labels. Reviewers assigned single, joint, insufficient or indeterminate and supplied a reason. Positive decisions included evidence excerpts. Both single and joint count as sufficient for the primary endpoint. Joint requires information from both passages. We retained disagreements and analysed each reader separately.

Table 1. Questions whose selected passages received credit. The Gold column uses annotated passage recovery. A and B apply the two readers' sufficiency decisions.


| Dataset | Retriever | Questions | Gold | A | B |
|---|---|---:|---:|---:|---:|
| HotpotQA | BM25 | 50 | 9 | 12 | 13 |
| HotpotQA | BGE | 50 | 24 | 24 | 26 |
| HotpotQA | BGE-title-link | 50 | 29 | 27 | 30 |
| MuSiQue | BM25 | 100 | 13 | 11 | 11 |
| MuSiQue | BGE | 100 | 26 | 25 | 26 |
| MuSiQue | BGE-title-link | 100 | 27 | 26 | 27 |

HotpotQA: the readers agreed on 102/105 binary decisions (Cohen’s kappa 0.94) and 102/105 four-category decisions. Compared with gold scoring, the change in the BGE minus BM25 gap was -6 points (95% interval -16 to 2) and -4 points (95% interval -14 to 6). Allowing every disputed sufficiency decision to take either reader’s value yields a BGE minus BM25 lead of 12 to 13 questions in this sample.

MuSiQue: the readers agreed on 197/198 binary decisions (Cohen’s kappa 0.98) and 197/198 four-category decisions. Compared with gold scoring, the change in the BGE minus BM25 gap was 1 point (95% interval -4 to 6) and 2 points (95% interval -3 to 7). Allowing every disputed sufficiency decision to take either reader’s value yields a BGE minus BM25 lead of 14 to 15 questions in this sample.

For a genuine two-passage alternative, consider the 1973 Pro Bowl question. A passage on the season identifies Arrowhead Stadium as the venue. A second passage identifies Arrowhead and Kauffman Stadium as the two venues in the Truman Sports Complex. The retrieved pair differs from the reference, yet both readers judged the combination sufficient. Conversely, both rejected a gold pair about two bands’ states of origin because it named the states but did not establish which state was larger. These cases illustrate two directions in which a passage-only judgement can depart from annotated recovery.

As a post hoc check suggested by one reviewer, we screened questions containing “what year” or “which year” for proposed answers lacking a four-digit year. One of the 150 questions met that rule. MuSiQue item 2hop__278022_71701 proposes November 5 for a question asking for a year. All three methods missed the annotated pair, and both readers rejected every retrieved set for that question. Removing it leaves the same successful-answer counts and the same ordering across the remaining 99 MuSiQue questions. Other forms of question–answer mismatch remain possible.

### 7. Limitations and next test
Both reviewers preserved the observed ordering on both datasets. Exact recovery and judged sufficiency sometimes awarded credit to different passage sets, but the intervals for changes in the primary BGE versus BM25 gap included zero for both readers and both datasets. These pilots establish concrete discrepancies at the item level. A systematic change in the size of the performance gap remains uncertain.

The sampled questions, candidate pools and two-passage budget restrict the conclusions to local reranking. The same model family, rubric and proposed answers can induce correlated judgement errors. High agreement measures consistency under those conditions. An answer shown to a reader may also encourage confirmation. The paired bootstrap resamples questions and treats reader labels as fixed. Its intervals omit uncertainty about the wider population of readers. Item-wise dispute bounds cover the observed disagreements only.

A human validation study should blind its readers to system identities, both AI decisions and the examples discussed here. Include a randomly sampled set of AI agreements alongside contested items to measure shared errors. A targeted disagreement sample alone cannot estimate accuracy over the audit. For a confirmatory system comparison, use questions disjoint from these pilots and fix scoring rules before viewing outputs.

### References
Trivedi et al. (2022). MuSiQue: Multihop Questions via Single-hop Question Composition. https://aclanthology.org/2022.tacl-1.31/

Yang et al. (2018). HotpotQA: A Dataset for Diverse, Explainable Multi-hop Question Answering. https://aclanthology.org/D18-1259/

Ni, Gardner and Dasigi (2021). Mitigating False-Negative Contexts in Multi-document Question Answering with Retrieval Marginalization. https://aclanthology.org/2021.emnlp-main.497/

Trivedi et al. (2020). Is Multihop QA in DiRe Condition? Measuring and Reducing Disconnected Reasoning. https://arxiv.org/abs/2005.00789
