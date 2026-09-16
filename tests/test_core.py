"""Small, deterministic checks; no Hugging Face data, model or GPU required."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from baselines import predict_doc
from eval_local import compute_metrics, load_predictions


class RuleBaselineTests(unittest.TestCase):
    def test_punctuation_paragraph_and_document_end(self):
        tokens = ["قال", "الطالب", ".", "\n", "عاد", "؟"]
        self.assertEqual(predict_doc(tokens, {"punct", "par"}, 13, True),
                         [0, 0, 1, 0, 0, 1])

    def test_verse_marker_and_document_end(self):
        self.assertEqual(predict_doc(["أ", "(", "12", ")", "ب"], {"verse"}, 13, True),
                         [0, 0, 0, 1, 1])

    def test_paragraph_token_never_gets_a_boundary(self):
        self.assertEqual(predict_doc(["عنوان", "\n"], {"par"}, 13, True), [1, 0])


class EvaluatorTests(unittest.TestCase):
    def test_document_macro_f1_and_positive_class(self):
        gold = {"a": [0, 1, 0, 1], "b": [0, 1]}
        pred = {"a": [0, 1, 0, 1], "b": [0, 0]}
        metrics = compute_metrics(gold, pred)
        self.assertAlmostEqual(metrics["macro_f1"], 0.5)
        self.assertAlmostEqual(metrics["macro_precision"], 0.5)
        self.assertAlmostEqual(metrics["macro_recall"], 0.5)

    def test_wrong_id_or_length_fails(self):
        with self.assertRaises(SystemExit):
            compute_metrics({"a": [1]}, {"b": [1]})
        with self.assertRaises(SystemExit):
            compute_metrics({"a": [1, 0]}, {"a": [1]})

    def test_duplicate_document_id_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "predictions.csv"
            path.write_text("Document ID,Prediction\na,01\na,11\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Duplicate"):
                load_predictions(str(path))

    def test_prediction_requires_nonempty_binary_string(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "predictions.csv"
            for content in ("Document ID,Prediction\na,01x\n",
                            "Document ID,Prediction\na,\n"):
                with self.subTest(content=content):
                    path.write_text(content, encoding="utf-8")
                    with self.assertRaises(ValueError):
                        load_predictions(str(path))


if __name__ == "__main__":
    unittest.main()
