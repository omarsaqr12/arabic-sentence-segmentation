# ENSAR: Noor Emam's jury-based extension

This repository retains the original AraSeg encoder-ensemble implementation in `src/` and includes [Noor Emam's ENSAR research repository](https://github.com/noortaytoy1/araseg-competition) as an **unchanged, commit-pinned Git submodule** at [`research/noor-ensar/`](../research/noor-ensar). The upstream commit is `122f50214f66c2dd5628a06fa2449783d7368e4b` (2026-09-11). A submodule keeps the complete upstream history, camera-version manuscript, policies, code, and experimental record attributable to its source. Changes to this repository's evaluator and tests do **not** rewrite upstream files or retroactively validate upstream results.

## What ENSAR adds

ENSAR first produces draft token-boundary decisions using the encoder ensemble and length-aware decoding. Two LLM juries, equipped with separate policy files learned from graded *training-split* errors, then examine each document's draft. Only edits both juries endorse are applied. Exact-index and exact-token checks reject mismatched edits; paragraph and document-end boundary invariants are restored before scoring. See [`jury/README.md`](../research/noor-ensar/jury/README.md), the [ENSAR manuscript](../research/noor-ensar/paper/ensar_araseg.tex), and the [source repository](https://github.com/noortaytoy1/araseg-competition).

**Attribution:** The ENSAR repository is maintained by [Noor Emam](https://github.com/noortaytoy1). Its manuscript lists Noor Emam, Omar Saqr, Mostafa Gafaar, and Aly El-aswad as authors. The current source has author-contact placeholders; do not infer individual contributions from a coauthor list. The original encoder work and Noor's subsequent jury work are presented as distinct stages; please consult the manuscript and commit history for exact authorship and provenance. Upstream licensing and external model/dataset terms still apply.

## Reproduce the released-test jury ablation, without making LLM calls

```bash
git clone --recurse-submodules https://github.com/omarsaqr12/arabic-sentence-segmentation.git
cd arabic-sentence-segmentation
# In an existing checkout instead: git submodule update --init research/noor-ensar
python -m pip install numpy
python src/data.py --task NoPnx-NP --out-dir data  # requires access to the public task dataset
bash scripts/ensar.sh replay NoPnx-NP data/NoPnx-NP_test.jsonl
```

`replay` uses Noor's **released** draft rows and already recorded verdicts, in a temporary folder, through Noor's strict scorer. It never calls an LLM or edits the source repository. The script requires the *matching official task split*, not the three-document `fixtures/PA_mini.jsonl` example. Run `bash scripts/ensar.sh help` for `packets` and `score` commands. To generate **new** jury verdicts, build a packet kit and follow upstream [`jury/REPLICATION.md`](../research/noor-ensar/jury/REPLICATION.md) and [`jury/orchestrator_prompt.txt`](../research/noor-ensar/jury/orchestrator_prompt.txt). The upstream `jury/run_exam.py` is explicitly marked an **untested**, potentially costly API approximation; this integration never invokes it automatically.

Upstream's `make probs` is **not** a verified one-command reproduction: as pinned, its `Makefile` invokes `src/cache_probs.py` without required `--split`, `--models` and `--out` arguments. The released-draft replay above bypasses this issue; regenerating voters and probabilities requires adapting upstream scripts and verifying model/checkpoint revisions. No GPU or LLM reproduction was run during this integration.

## Do not conflate the different score populations

Noor's repository reports these **released-test ablations**, scored over 262 documents per task using saved verdicts. These numbers are transcribed from Noor's README, **not independently recomputed here**:

| Track | Ensemble macro-F1 | Ensemble + jury macro-F1 |
| --- | ---: | ---: |
| NoPnx-NP | 84.64 | 89.49 |
| NoPnx-PA | 87.05 | 92.59 |
| NP (Pnx-NP) | 92.83 | 93.61 |
| PA (Pnx-PA) | 94.56 | 94.92 |

They are **not the official blind-submission scores** and must not be substituted for them. In particular, the released-test NoPnx-PA doctrine was retrained on all 174 training documents **after** the submission deadline; the blind submission used a different, less-trained pair. Noor's [`CONTAMINATION_MAP.md`](../research/noor-ensar/CONTAMINATION_MAP.md) reports an earlier dev/test exposure in a superseded jury-training wave, the subsequent purge and clean-room retraining, and the limits of the resulting evidence. Read that audit before repeating any blind-ranking or clean-room claim. The stored-verdict replay tests the public scoring artifact; it does not independently establish training purity, blind leaderboard positions, model generalization or the manuscript's complete 224-check assertion.

## Maintenance boundaries

- `src/`, `tests/`, and the existing `paper/araseg_system.*`: original encoder research and locally reviewed fixes.
- `research/noor-ensar/`: the complete **pinned** external research snapshot, not a vendor copy to edit casually. To update it, review a newer upstream commit and explicitly advance the gitlink in a separate PR.
- `scripts/ensar.sh`: a thin integration for packet creation and read-only scoring; all substantive jury implementation remains upstream.
- The root `CITATION.cff` and original ACL-template source have previously noted attribution/compilation issues. Neither is silently repaired by adding the ENSAR submodule; cite the appropriate manuscript after author review.
