"""Small integration contract for the pinned ENSAR submodule; not a paper reproduction."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENSAR = ROOT / "research" / "noor-ensar"
PIN = "122f50214f66c2dd5628a06fa2449783d7368e4b"
TRACKS = ("PA", "NP", "NoPnx-PA", "NoPnx-NP")


@unittest.skipUnless((ENSAR / "jury" / "build_packets.py").is_file(),
                     "ENSAR submodule not initialized; run git submodule update --init research/noor-ensar")
class ENSARIntegrationTests(unittest.TestCase):
    def test_gitlink_revision_is_exactly_pinned(self):
        revision = subprocess.check_output(
            ["git", "-C", str(ENSAR), "rev-parse", "HEAD"], text=True
        ).strip()
        self.assertEqual(revision, PIN)

    def test_released_verdict_files_cover_each_reported_test_set(self):
        for track in TRACKS:
            with self.subTest(track=track):
                verdicts = list((ENSAR / "jury" / "verdicts_test" / track).glob("doc_*.json"))
                self.assertEqual(len(verdicts), 262)
                self.assertTrue((ENSAR / "jury" / "draft_rows" / (track + ".json")).is_file())

    def test_packet_generation_excludes_gold_and_strict_scorer_accepts_verdicts(self):
        docs = [
            {"doc_id": "sample_1", "tokens": ["ذهب", "الطالب", "."], "labels": [0, 0, 1]},
            {"doc_id": "sample_2", "tokens": ["قال", "مرحبا", ".", "\n", "عاد", "."],
             "labels": [0, 0, 1, 0, 0, 1]},
        ]
        with tempfile.TemporaryDirectory() as work:
            root = Path(work)
            gold = root / "gold.jsonl"
            gold.write_text("\n".join(json.dumps(d, ensure_ascii=False) for d in docs) + "\n",
                            encoding="utf-8")
            draft = root / "draft.json"
            draft.write_text(json.dumps({"rows": {
                "sample_1": "000", "sample_2": "000000"
            }}), encoding="utf-8")
            kit = root / "kit"
            subprocess.run([sys.executable, str(ENSAR / "jury/build_packets.py"),
                            "--track", "PA", "--data", str(gold),
                            "--draft", str(draft), "--out", str(kit)],
                           check=True, capture_output=True, text=True)
            manifest = json.loads((kit / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["docs"], ["sample_1", "sample_2"])
            for doc in docs:
                packet = json.loads((kit / "docs" / (doc["doc_id"] + ".json")).read_text(
                    encoding="utf-8"))
                self.assertEqual(set(packet), {"doc_id", "text"})
                self.assertNotIn("labels", packet)
                (kit / "out" / (doc["doc_id"] + ".json")).write_text(
                    json.dumps({"doc_id": doc["doc_id"], "add": [], "remove": []}),
                    encoding="utf-8")
            result = subprocess.run([sys.executable, str(ENSAR / "jury/score/score_kit.py"),
                                     "--track", "PA", "--kit", str(kit),
                                     "--gold", str(gold), "--draft", str(draft)],
                                    check=True, capture_output=True, text=True)
            self.assertIn("n=2 documents with verdicts", result.stdout)
            self.assertIn("delta +0.00", result.stdout)


if __name__ == "__main__":
    unittest.main()
