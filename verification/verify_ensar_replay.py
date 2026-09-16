"""Replay pinned ENSAR released-test verdicts against the public official test splits.

No model training, paid LLM calls or blind-leaderboard verification. The four
expected rows are the paper's *released-test ablations*, not official blind scores.
Run: python -m pip install 'datasets==3.6.0' 'numpy<3' && python verification/verify_ensar_replay.py
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from datasets import load_dataset

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / "research" / "noor-ensar"
PIN = "122f50214f66c2dd5628a06fa2449783d7368e4b"
# Track -> (Hugging Face repo, recorded ensemble F1, recorded jury F1)
TRACKS = {
    "NoPnx-NP": ("MBZUAI/AraSeg-2026-Shared-Task-NoPnx-NP", 84.64, 89.49),
    "NoPnx-PA": ("MBZUAI/AraSeg-2026-Shared-Task-NoPnx-PA", 87.05, 92.59),
    "NP": ("MBZUAI/AraSeg-2026-Shared-Task-NP", 92.83, 93.61),
    "PA": ("MBZUAI/AraSeg-2026-Shared-Task-PA", 94.56, 94.92),
}


def main() -> int:
    if not (UPSTREAM / "jury/score/score_kit.py").is_file():
        raise RuntimeError("Initialize ENSAR with git submodule update --init research/noor-ensar")
    rev = subprocess.check_output(["git", "-C", str(UPSTREAM), "rev-parse", "HEAD"], text=True).strip()
    if rev != PIN:
        raise ValueError(f"ENSAR revision is {rev}; expected immutable release {PIN}")
    failures = []
    with tempfile.TemporaryDirectory(prefix="ensar-public-test-") as td:
        tmp = Path(td)
        for track, (dataset, expected_base, expected_jury) in TRACKS.items():
            docs = [dict(d) for d in load_dataset(dataset, split="test")]
            ids = [d["doc_id"] for d in docs]
            if len(ids) != 262 or len(set(ids)) != 262:
                raise ValueError(f"{track}: expected 262 unique public test documents; got {len(ids)}")
            draft = UPSTREAM / "jury/draft_rows" / f"{track}.json"
            rows = json.loads(draft.read_text(encoding="utf-8"))["rows"]
            verdict_dir = UPSTREAM / "jury/verdicts_test" / track
            verdicts = sorted(verdict_dir.glob("doc_*.json"))
            verdict_ids = [p.stem for p in verdicts]
            if set(ids) != set(rows) or set(ids) != set(verdict_ids):
                raise ValueError(f"{track}: public test IDs, released draft IDs and verdict IDs differ")
            for d in docs:
                marks = rows[d["doc_id"]]
                if not marks or set(marks) - {"0", "1"} or len(marks) != len(d["tokens"]):
                    raise ValueError(f"{track}: invalid or wrong-length draft for {d['doc_id']}")
                if len(d["labels"]) != len(d["tokens"]):
                    raise ValueError(f"{track}: bad public gold for {d['doc_id']}")
            kit = tmp / track
            (kit / "out").mkdir(parents=True)
            gold = kit / "public_test.jsonl"
            with gold.open("w", encoding="utf-8") as f:
                for d in docs:
                    f.write(json.dumps(d, ensure_ascii=False) + "\n")
            for p in verdicts:
                shutil.copyfile(p, kit / "out" / p.name)
            proc = subprocess.run([
                sys.executable, str(UPSTREAM / "jury/score/score_kit.py"),
                "--track", track, "--kit", str(kit), "--gold", str(gold),
                "--draft", str(draft),
            ], check=True, capture_output=True, text=True)
            out = proc.stdout
            if "n=262 documents with verdicts" not in out:
                raise ValueError(f"{track}: scorer did not evaluate all 262 documents: {out}")
            base = re.search(r"ensemble \(draft\):\s*([\d.]+)", out)
            jury = re.search(r"\+ juries\s*:\s*([\d.]+)", out)
            if not base or not jury:
                raise ValueError(f"{track}: cannot parse strict scorer output: {out}")
            measured = (float(base.group(1)), float(jury.group(1)))
            expected = (expected_base, expected_jury)
            print(f"{track}: strict saved-verdict replay {measured[0]:.2f} -> {measured[1]:.2f}; "
                  f"paper {expected_base:.2f} -> {expected_jury:.2f}", flush=True)
            if any(abs(got - claimed) > 0.015 for got, claimed in zip(measured, expected)):
                failures.append((track, expected, measured))
    if failures:
        for track, expected, measured in failures:
            print(f"MISMATCH {track}: recorded={expected}, replay={measured}", file=sys.stderr)
        return 1
    print("PASS: four public released-test ablations independently replayed from pinned verdicts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
