"""Fetch the gated AraSeg-2026 blind test sets from HuggingFace and dump them
to raw/<task>_blind.jsonl in the schema prepare_blind.py expects.

Auth: run `hf auth login` once, in your own terminal, before this script.
Never pass a token as a CLI argument or hardcode it here — load_dataset(...,
token=True) reads the cached login automatically.

Usage:
  python fetch_blind_hf.py --inspect        # print schema + one sample row per task, write nothing
  python fetch_blind_hf.py                  # fetch all 4 and write raw/<task>_blind.jsonl
"""
from __future__ import annotations

import argparse
import json
import os

from datasets import load_dataset

TASKS = {
    "PA": "MBZUAI/AraSeg-2026-Shared-Task-PA-Blind",
    "NP": "MBZUAI/AraSeg-2026-Shared-Task-NP-Blind",
    "NoPnx-PA": "MBZUAI/AraSeg-2026-Shared-Task-NoPnx-PA-Blind",
    "NoPnx-NP": "MBZUAI/AraSeg-2026-Shared-Task-NoPnx-NP-Blind",
}


def pick_split(ds):
    if hasattr(ds, "keys"):
        for k in ("test", "blind", "train"):
            if k in ds:
                return ds[k]
        return ds[list(ds.keys())[0]]
    return ds


def row_to_doc(i, r):
    did = r.get("doc_id") or r.get("id") or r.get("document_id") or r.get("Id")
    if did is None:
        did = str(i)
    toks = r.get("tokens")
    if toks is None:
        toks = r.get("words")
    text = r.get("text")
    return did, toks, text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inspect", action="store_true",
                     help="print schema + sample only, write nothing")
    ap.add_argument("--out-dir", default="raw")
    a = ap.parse_args()

    for task, name in TASKS.items():
        print(f"== {task} ({name}) ==")
        ds = load_dataset(name, token=True)
        split = pick_split(ds)
        print(f"  {len(split)} rows, columns={split.column_names}")
        sample = {k: str(v)[:150] for k, v in split[0].items()}
        print(f"  sample: {sample}")
        if a.inspect:
            continue
        os.makedirs(a.out_dir, exist_ok=True)
        out_path = os.path.join(a.out_dir, f"{task}_blind.jsonl")
        n = 0
        with open(out_path, "w") as f:
            for i, r in enumerate(split):
                did, toks, text = row_to_doc(i, r)
                rec = {"doc_id": str(did)}
                if toks is not None:
                    rec["tokens"] = [str(t) for t in toks]
                elif text is not None:
                    rec["text"] = text
                else:
                    raise SystemExit(f"row {i} has neither tokens/words nor text: keys={list(r)}")
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                n += 1
        print(f"  wrote {n} docs -> {out_path}")


if __name__ == "__main__":
    main()
