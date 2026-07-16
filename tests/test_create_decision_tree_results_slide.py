import csv
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from pptx import Presentation

from scripts.create_decision_tree_results_slide import create_results_slide


def _metrics(accuracy, recalls, parameters):
    return {
        "accuracy": accuracy,
        "labels": list(range(8)),
        "support": {str(label): value for label, value in enumerate([1, 2, 3, 4, 5, 6, 7, 0])},
        "recall": {str(label): recall for label, recall in enumerate(recalls)},
        "periods": {"train": [1995, 2023], "test": [2024, 2026]},
        "train_rows": 100,
        "test_rows": 28,
        "selected_parameters": parameters,
    }


class DecisionTreeResultsSlideTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        self.decision_tree = _metrics(
            0.2833168806,
            [0.0, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, None],
            {"max_depth": 12, "min_samples_leaf": 1},
        )
        self.random_forest = _metrics(
            0.4389601843,
            [0.0, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, None],
            {"n_estimators": 200, "max_depth": 12, "min_samples_leaf": 1},
        )
        self.decision_tree_path = self.root / "decision-tree.json"
        self.random_forest_path = self.root / "random-forest.json"
        self.comparison_path = self.root / "comparison.csv"
        self.output = self.root / "review.pptx"
        self.decision_tree_path.write_text(json.dumps(self.decision_tree), encoding="utf-8")
        self.random_forest_path.write_text(json.dumps(self.random_forest), encoding="utf-8")
        self._write_comparison()

    def tearDown(self):
        self.directory.cleanup()

    def _write_comparison(self, random_forest_accuracy=0.4389601843, random_forest_macro_recall=None):
        fields = ["model", "accuracy", "macro_recall"]
        for label in range(8):
            fields.extend([f"recall_{label}", f"support_{label}"])
        with self.comparison_path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            for model, metrics, accuracy in (
                ("decision_tree", self.decision_tree, self.decision_tree["accuracy"]),
                ("random_forest", self.random_forest, random_forest_accuracy),
            ):
                row = {
                    "model": model,
                    "accuracy": accuracy,
                    "macro_recall": sum(value for value in metrics["recall"].values() if value is not None) / 7,
                }
                if model == "random_forest" and random_forest_macro_recall is not None:
                    row["macro_recall"] = random_forest_macro_recall
                for label in range(8):
                    row[f"recall_{label}"] = "" if metrics["recall"][str(label)] is None else metrics["recall"][str(label)]
                    row[f"support_{label}"] = metrics["support"][str(label)]
                writer.writerow(row)

    def test_creates_one_widescreen_two_model_slide(self):
        create_results_slide(
            self.decision_tree_path,
            self.random_forest_path,
            self.comparison_path,
            self.output,
        )

        with zipfile.ZipFile(self.output) as package:
            self.assertIsNone(package.testzip())
            self.assertEqual(
                len([name for name in package.namelist() if name.startswith("ppt/slides/slide") and name.endswith(".xml")]),
                1,
            )
        deck = Presentation(self.output)
        self.assertEqual(len(deck.slides), 1)
        self.assertAlmostEqual(deck.slide_width / deck.slide_height, 16 / 9, places=2)
        text = "\n".join(shape.text for shape in deck.slides[0].shapes if hasattr(shape, "text"))
        for expected in ("決策樹", "隨機森林", "Accuracy", "Macro Recall", "稀有類別", "28.33%", "43.90%"):
            self.assertIn(expected, text)

    def test_rejects_comparison_values_that_disagree_with_metrics(self):
        self._write_comparison(random_forest_accuracy=0.9)

        with self.assertRaisesRegex(ValueError, "comparison.*random_forest.*accuracy"):
            create_results_slide(
                self.decision_tree_path,
                self.random_forest_path,
                self.comparison_path,
                self.output,
            )

    def test_rejects_comparison_macro_recall_that_disagrees_with_metrics(self):
        self._write_comparison(random_forest_macro_recall=0.9)

        with self.assertRaisesRegex(ValueError, "comparison.*random_forest.*macro_recall"):
            create_results_slide(
                self.decision_tree_path,
                self.random_forest_path,
                self.comparison_path,
                self.output,
            )


if __name__ == "__main__":
    unittest.main()
