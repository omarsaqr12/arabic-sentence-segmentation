# Arabic Sentence Segmentation — AraSeg 2026

[![fixture-smoke-test](https://github.com/omarsaqr12/arabic-sentence-segmentation/actions/workflows/smoke.yml/badge.svg)](https://github.com/omarsaqr12/arabic-sentence-segmentation/actions/workflows/smoke.yml)

**Research code | Arabic NLP | PyTorch / Hugging Face | structured decoding + LLM jury refinement**

Given an Arabic document, predict whether a sentence ends after **each whitespace token**. The [AraSeg 2026 shared task](https://www.araseg.aramlab.ai/) evaluates four conditions crossing the presence or absence of punctuation and paragraph boundaries. This repository documents two complementary research stages: an Arabic encoder ensemble with length-aware decoding, and **ENSAR**, a subsequent jury-based error-refinement system developed in [Noor Emam's research repository](https://github.com/noortaytoy1/araseg-competition).

**Start here:** [ENSAR integration and reproducibility](docs/ENSAR_INTEGRATION.md) · [original CPU-only fixture](#quickstart-no-dataset-or-gpu) · [ensemble experiment log](docs/EXPERIMENTS.md) · [original system paper](paper/araseg_system.pdf) · [core inference](src/predict.py)

## Two-stage system and provenance

1. **Encoder ensemble (this repository's `src/`):** fine-tune Arabic token classifiers, average their boundary probabilities, and apply a train-fit sentence-length prior with structurally constrained decoding. The experiment record investigates diminishing returns from model scaling and ensemble additions.
2. **ENSAR (pinned [`research/noor-ensar/`](research/noor-ensar/)):** two LLM juries use separately learned, train-error-derived policies to review the ensemble draft, retaining only edits both endorse. The submodule preserves Noor's complete source, jury policies, recorded verdicts, provenance audit and [ENSAR manuscript](research/noor-ensar/paper/ensar_araseg.tex) at the exact reviewed upstream commit. Its original code and data are not silently mixed into or substituted for the encoder implementation.

The jury work is attributed to **[Noor Emam](https://github.com/noortaytoy1)** and the ENSAR manuscript's author team. See the [integration guide](docs/ENSAR_INTEGRATION.md) for the stage boundaries, original-source attribution, recorded released-test ablations, the documented contamination/remediation history, and a read-only replay procedure. A standard clone needs `git submodule update --init research/noor-ensar` (or clone with `--recurse-submodules`) to obtain ENSAR; GitHub's web UI shows the pinned submodule link without downloading its contents into this repository's main tree.

## Recorded ensemble results and evidence

The earlier README records the following **CodaBench development-phase** closed-track results under the `omar_saqr` submission name. These are historical results as reported in this repository, **not independently rechecked final leaderboard placements** and not reproduced by the small CI fixture.

| Task | Input structure | Recorded closed-track F1 | Organizer baseline recorded in repo |
| --- | --- | ---: | ---: |
| PA | Punctuation and paragraphs | 94.4 | 92.8 |
| NoPnx-PA | Paragraphs, no punctuation | 87.4 | 82.8 |
| NP | Punctuation, no paragraphs | 92.9 | 89.7 |
| NoPnx-NP | Neither punctuation nor paragraphs | 85.0 | 77.8 |

The original record reports first place on all four **development-phase** closed-track boards. This must not be confused with ENSAR's later *official blind-submission scores* or its *released-test ablations*, which involve different conditions and, for NoPnx-PA, a post-deadline retrained jury pair. The [ensemble experiment log](docs/EXPERIMENTS.md) records configurations, seeds, dev/test results where available, failed approaches and selection decisions. Model checkpoints, cached probabilities, submission CSVs, raw datasets and GPU logs are **not committed to the original repository**.

## Architecture: follow the data

1. [`src/data.py`](src/data.py) reads one of four task datasets or an offline JSONL export; `\n` paragraph markers are tokens rather than ordinary whitespace.
2. [`src/train_encoder.py`](src/train_encoder.py) fine-tunes a token classifier, assigning each word's boundary label to its last subword and masking other subwords.
3. [`src/predict.py`](src/predict.py) predicts over overlapping document windows, averages probabilities for covered words, forces paragraph-marker labels to zero and writes submission CSVs.
4. [`src/cache_probs.py`](src/cache_probs.py), [`src/ensemble_sweep.py`](src/ensemble_sweep.py), [`src/dp_decode.py`](src/dp_decode.py) and [`src/dp_adaptive.py`](src/dp_adaptive.py) support the ensemble and structured-decoding studies.
5. [`research/noor-ensar/jury/`](research/noor-ensar/jury/) contains ENSAR's policy training record, packet construction, jury prompts, strict application/scoring, and saved verdicts. [`scripts/ensar.sh`](scripts/ensar.sh) exposes safe packet, scoring and **no-LLM replay** entry points.
6. [`src/eval_local.py`](src/eval_local.py) scores per-document boundary-class precision, recall and F1 and rejects ID, length and malformed-prediction errors.

For the original encoder research workflow, see [`docs/PLAYBOOK.md`](docs/PLAYBOOK.md), [`docs/RUNBOOK_BLIND_TEST.md`](docs/RUNBOOK_BLIND_TEST.md) and [`docs/EXPERIMENTS.md`](docs/EXPERIMENTS.md). Historical shell experiments live in [`scripts/`](scripts/); inspect paths, model requirements and compute demands before executing them.

## Quickstart: no dataset or GPU

From a checkout with Python 3.10 installed, exercise the original baseline/evaluator on the checked-in three-document JSONL fixture:

```bash
python -m pip install pandas numpy scikit-learn
python src/baselines.py --task PA --jsonl fixtures/PA_mini.jsonl \
  --rules punct verse par --out /tmp/araseg_fixture.csv
python src/eval_local.py --task PA --gold-jsonl fixtures/PA_mini.jsonl \
  --predictions /tmp/araseg_fixture.csv --show-worst 2
python -m unittest discover -s tests -v
```

CI checks the original baseline, evaluator and behavioral regressions, and the ENSAR submodule integration. **A passing fixture, syntax check or recorded-verdict replay does not reproduce training or prove an external leaderboard claim.** For ENSAR's saved-verdict, no-LLM replay, initialize the submodule and follow [`docs/ENSAR_INTEGRATION.md`](docs/ENSAR_INTEGRATION.md).

## Training and full reproduction

For original encoder experiments, install [`requirements.txt`](requirements.txt), obtain the four [MBZUAI AraSeg task datasets](https://huggingface.co/MBZUAI), and consult the [official starter/evaluator](https://github.com/mbzuai-nlp/araseg-shared-task-2026) and [playbook](docs/PLAYBOOK.md). For example, after obtaining data and a suitable PyTorch/GPU environment:

```bash
python src/data.py --task PA --out-dir data
python src/train_encoder.py --task PA --out-dir runs/pa
python src/predict.py --model runs/pa --task PA --split dev \
  --out subs/PA_dev.csv
python src/eval_local.py --task PA --split dev --predictions subs/PA_dev.csv
```

These commands train **one** model, not the full published ensemble or ENSAR. Exact model identities, seed selections, threshold/decode choices and required artifacts are detailed in the respective experiment records. A fresh-checkout GPU/LLM reproduction and external score verification have **not** been performed in this integration. The submission schema is `Document ID,Prediction` with one binary character per token, including paragraph markers. Use `src/predict.py --check-ids PATH_TO_OFFICIAL_EXAMPLE.csv` to compare IDs and lengths with the official example file.

## Papers, authorship and limitations

The original standalone paper is [`paper/araseg_system.pdf`](paper/araseg_system.pdf), with source in [`paper/araseg_system.tex`](paper/araseg_system.tex). The newer [ENSAR manuscript](research/noor-ensar/paper/ensar_araseg.tex) is **a separate work**; its source lists Noor Emam, Omar Saqr, Mostafa Gafaar and Aly El-aswad, with contact details still requiring author verification. Do not treat the original [`paper/acl/araseg_acl.tex`](paper/acl/araseg_acl.tex) as a ready-to-submit ACL file: the tracked source has duplicate LaTeX preambles and an author-list TODO. The root [`CITATION.cff`](CITATION.cff) also has unresolved author metadata and should not be reused as the ENSAR citation. No manuscript authorship or publication status was silently changed.

The root [MIT license](LICENSE) covers the original repository code; the pinned ENSAR submodule carries its own upstream license and history. Third-party datasets, pretrained checkpoints and hosted LLMs have separate access, use and cost terms. ENSAR's recorded scores are subject to the provenance and remediation details in its [`CONTAMINATION_MAP.md`](research/noor-ensar/CONTAMINATION_MAP.md); the integration does not independently verify them or imply deployment readiness.
