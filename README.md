# Arabic Sentence Segmentation — AraSeg 2026

[![fixture-smoke-test](https://github.com/omarsaqr12/arabic-sentence-segmentation/actions/workflows/smoke.yml/badge.svg)](https://github.com/omarsaqr12/arabic-sentence-segmentation/actions/workflows/smoke.yml)

**Research code | Arabic NLP | PyTorch / Hugging Face | sentence-boundary detection**

Given an Arabic document, predict whether a sentence ends after **each whitespace token**. The [AraSeg 2026 shared task](https://www.araseg.aramlab.ai/) evaluates four conditions crossing the presence or absence of punctuation and paragraph boundaries. This repository contains fine-tuning, inference, probability ensembling, length-aware decoding, offline evaluation and an experiment record. The interesting engineering question is not simply whether a larger model scores higher: it is how to improve a boundary detector when training data are scarce and the ensemble's gains have mostly saturated.

**Start here:** [run a CPU-only fixture](#quickstart-no-dataset-or-gpu) · [experiment log](docs/EXPERIMENTS.md) · [end-to-end playbook](docs/PLAYBOOK.md) · [system-paper PDF](paper/araseg_system.pdf) · [core inference](src/predict.py)

## Recorded results and evidence

The prior README records the following **CodaBench development-phase** closed-track results under the `omar_saqr` submission name. These are historical, task-specific results as reported in this repository, **not independently rechecked current leaderboard placements** or reproduced by the small CI fixture.

| Task | Input structure | Recorded closed-track F1 | Organizer baseline recorded in repo |
| --- | --- | ---: | ---: |
| PA | Punctuation and paragraphs | 94.4 | 92.8 |
| NoPnx-PA | Paragraphs, no punctuation | 87.4 | 82.8 |
| NP | Punctuation, no paragraphs | 92.9 | 89.7 |
| NoPnx-NP | Neither punctuation nor paragraphs | 85.0 | 77.8 |

The original submission record reports first place on all four **development-phase** closed-track boards. This should not be interpreted as a final shared-task ranking. The [experiment log](docs/EXPERIMENTS.md) includes configurations, seeds, dev/test scores where recorded, failed approaches and selection decisions. Model checkpoints, cached probabilities, submission CSVs, raw datasets and GPU logs are **not committed**; the numerical claims therefore cannot be independently regenerated from this checkout alone.

The system combines Arabic encoders (AraBERT, AraELECTRA and ARBERT) by averaging token-boundary probabilities and uses a semi-Markov dynamic program with a sentence-length prior fit on the training split. The code also explores source-data pretraining, alternative encoders, calibration, augmentation and bootstrap-based model selection. The manuscript argues that additional capacity and closely correlated voters often give little benefit under this data regime; its scaling and ambiguity analyses are **research interpretations of the recorded experiments**, not universally established limits on Arabic segmentation.

## Architecture: follow the data

1. [`src/data.py`](src/data.py) reads one of four task datasets or an offline JSONL export; `\n` paragraph markers are tokens rather than ordinary whitespace.
2. [`src/train_encoder.py`](src/train_encoder.py) fine-tunes a token classifier, assigning each word's boundary label to its last subword and masking other subwords.
3. [`src/predict.py`](src/predict.py) predicts over overlapping document windows, averages probabilities for covered words, forces paragraph-marker labels to zero and writes submission CSVs.
4. [`src/cache_probs.py`](src/cache_probs.py), [`src/ensemble_sweep.py`](src/ensemble_sweep.py), [`src/dp_decode.py`](src/dp_decode.py) and [`src/dp_adaptive.py`](src/dp_adaptive.py) support the ensemble and structured-decoding studies.
5. [`src/eval_local.py`](src/eval_local.py) scores per-document boundary-class precision, recall and F1, checks document IDs and token counts, and now rejects duplicate IDs and malformed predictions.

For the research workflow and per-run command history, see [`docs/PLAYBOOK.md`](docs/PLAYBOOK.md), [`docs/RUNBOOK_BLIND_TEST.md`](docs/RUNBOOK_BLIND_TEST.md), and [`docs/EXPERIMENTS.md`](docs/EXPERIMENTS.md). Historical shell experiments live in [`scripts/`](scripts/); inspect their paths, model requirements and compute demands before executing them.

## Quickstart: no dataset or GPU

From a checkout with Python 3.10 installed, this exercises the actual baseline and evaluator on the checked-in three-document JSONL fixture:

```bash
python -m pip install pandas numpy scikit-learn
python src/baselines.py --task PA --jsonl fixtures/PA_mini.jsonl \
  --rules punct verse par --out /tmp/araseg_fixture.csv
python src/eval_local.py --task PA --gold-jsonl fixtures/PA_mini.jsonl \
  --predictions /tmp/araseg_fixture.csv --show-worst 2
python -m unittest discover -s tests -v
```

CI additionally compiles all `src/*.py`. The regression tests assert boundary-rule behavior, the boundary-class macro metric, ID/length checks and malformed/duplicate CSV rejection. **A passing fixture or syntax check does not reproduce the trained models or leaderboard scores.**

## Training and full reproduction

For model experiments, install the dependencies in [`requirements.txt`](requirements.txt), obtain the four [MBZUAI AraSeg task datasets](https://huggingface.co/MBZUAI), and consult the [official starter/evaluator](https://github.com/mbzuai-nlp/araseg-shared-task-2026) and [playbook](docs/PLAYBOOK.md). For example, after obtaining the necessary access and a suitable PyTorch/GPU environment:

```bash
python src/data.py --task PA --out-dir data
python src/train_encoder.py --task PA --out-dir runs/pa
python src/predict.py --model runs/pa --task PA --split dev \
  --out subs/PA_dev.csv
python src/eval_local.py --task PA --split dev --predictions subs/PA_dev.csv
```

The sample commands train **one** model; they do not recreate the complete published ensemble. Exact model identities, seed selections, threshold/decode choices and required artifacts are detailed in the experiment log. A full fresh-checkout reproduction and external score verification have **not** been performed as part of this repository refinement.

The submission schema is `Document ID,Prediction` with one binary character per token, including paragraph markers. Use `src/predict.py --check-ids PATH_TO_OFFICIAL_EXAMPLE.csv` to compare IDs and lengths with an official example file; this flag needs an explicit path.

## Paper, attribution and limitations

The standalone manuscript is [`paper/araseg_system.pdf`](paper/araseg_system.pdf), with source in [`paper/araseg_system.tex`](paper/araseg_system.tex). **Do not treat [`paper/acl/araseg_acl.tex`](paper/acl/araseg_acl.tex) as a ready-to-submit ACL source:** its tracked version contains duplicate LaTeX preambles/document starts and a TODO to verify the author list. The author name in [`CITATION.cff`](CITATION.cff) also needs confirmation against the intended publication record before that metadata is used for citation. Neither manuscript authorship nor its publication status is inferred or changed here.

This repository's [MIT license](LICENSE) covers the repository code, not third-party datasets or pretrained checkpoints. The dataset, official evaluator and pretrained models have their own access and reuse terms. Results depend on the shared-task splits, external model versions and uncommitted checkpoints. The CPU fixture covers correctness of a small path, **not** generalization, leaderboard status or deployment readiness.
