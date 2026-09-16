#!/usr/bin/env bash
# Thin bridge to Noor Emam's immutable ENSAR submodule. No API/LLM calls here.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENSAR="$ROOT/research/noor-ensar"
PY="${PYTHON:-python3}"

usage() {
  cat <<'USAGE'
Usage (run from any directory):
  bash scripts/ensar.sh packets TRACK GOLD_JSONL OUTPUT_KIT
  bash scripts/ensar.sh score   TRACK GOLD_JSONL EXISTING_KIT
  bash scripts/ensar.sh replay  TRACK GOLD_JSONL
  bash scripts/ensar.sh help

TRACK: PA | NP | NoPnx-PA | NoPnx-NP
packets: build packets using Noor's exact released draft rows and doctrine pair.
score: score verdicts already present in EXISTING_KIT/out/ using Noor's strict scorer.
replay: score Noor's already-released verdicts in a temporary directory (no LLM calls).
These are released-test research ablations, NOT blind leaderboard verification.
USAGE
}

if [[ "${1:-}" == help || $# -eq 0 ]]; then
  usage
  exit 0
fi
operation="$1"
shift
case "$operation" in packets|score|replay) ;; *) usage >&2; exit 2 ;; esac
case "$operation" in
  packets|score) [[ $# -eq 3 ]] || { usage >&2; exit 2; } ;;
  replay) [[ $# -eq 2 ]] || { usage >&2; exit 2; } ;;
esac
track="$1"
gold="$2"
case "$track" in PA|NP|NoPnx-PA|NoPnx-NP) ;; *) echo "Unsupported track: $track" >&2; exit 2 ;; esac
if [[ ! -f "$ENSAR/jury/build_packets.py" ]]; then
  echo "ENSAR is not initialized. Run: git submodule update --init research/noor-ensar" >&2
  exit 2
fi
if [[ ! -f "$gold" ]]; then
  echo "Missing matching official task JSONL: $gold" >&2
  exit 2
fi
draft="$ENSAR/jury/draft_rows/$track.json"
[[ -f "$draft" ]] || { echo "Missing upstream draft rows: $draft" >&2; exit 2; }

case "$operation" in
  packets)
    kit="$3"
    "$PY" "$ENSAR/jury/build_packets.py" --track "$track" --split test \
      --data "$gold" --draft "$draft" --out "$kit"
    ;;
  score)
    kit="$3"
    [[ -d "$kit/out" ]] || { echo "Missing verdict directory: $kit/out" >&2; exit 2; }
    "$PY" "$ENSAR/jury/score/score_kit.py" --track "$track" \
      --kit "$kit" --gold "$gold" --draft "$draft"
    ;;
  replay)
    tmp="$(mktemp -d)"
    trap 'rm -rf -- "$tmp"' EXIT
    mkdir -p "$tmp/out"
    verdicts="$ENSAR/jury/verdicts_test/$track"
    [[ -d "$verdicts" ]] || { echo "Missing released verdicts: $verdicts" >&2; exit 2; }
    # Only individual document verdicts, not ablation summary JSONs.
    cp -- "$verdicts"/doc_*.json "$tmp/out/"
    count="$(find "$tmp/out" -maxdepth 1 -name 'doc_*.json' -type f | wc -l)"
    [[ "$count" -eq 262 ]] || { echo "Expected 262 released verdicts; found $count" >&2; exit 1; }
    "$PY" "$ENSAR/jury/score/score_kit.py" --track "$track" \
      --kit "$tmp" --gold "$gold" --draft "$draft"
    ;;
esac
