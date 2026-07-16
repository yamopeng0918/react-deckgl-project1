import copy
import csv
import json
import tempfile
import unittest
from pathlib import Path

from scripts.compare_intensity_models import (
    build_comparison_rows,
    load_metrics,
    macro_recall,
    run_pipeline,
    validate_comparable_metrics,
)


def sample_metrics(accuracy=0.5, recall_offset=0.0):
    return {
        "accuracy": accuracy,
        "periods": {"test": [2024, 2026]},
        "test_rows": 8,
        "labels": list(range(8)),
        "support": {str(label): 1 for label in range(8)},
        "recall": {
            str(label): (label / 10) + recall_offset for label in range(8)
        },
    }


class ModelComparisonTest(unittest.TestCase):
    def test_builds_decision_tree_then_random_forest_rows(self):
        tree = sample_metrics(accuracy=0.25)
        forest = sample_metrics(accuracy=0.75, recall_offset=0.1)

        rows = build_comparison_rows(tree, forest)

        self.assertEqual([row["model"] for row in rows], ["decision_tree", "random_forest"])
        self.assertEqual(rows[0]["accuracy"], 0.25)
        self.assertAlmostEqual(rows[0]["macro_recall"], 0.35)
        self.assertAlmostEqual(rows[1]["recall_7"], 0.8)
        self.assertEqual(rows[1]["support_7"], 1)

    def test_rejects_each_comparable_field_mismatch(self):
        mutations = {
            "periods.test": lambda metrics: metrics["periods"].__setitem__("test", [2025, 2026]),
            "test_rows": lambda metrics: metrics.__setitem__("test_rows", 9),
            "labels": lambda metrics: metrics.__setitem__("labels", list(reversed(range(8)))),
            "support": lambda metrics: metrics["support"].__setitem__("7", 2),
        }
        tree = sample_metrics()
        for field, mutate in mutations.items():
            with self.subTest(field=field):
                forest = copy.deepcopy(tree)
                mutate(forest)
                with self.assertRaisesRegex(ValueError, field.replace(".", r"\.")):
                    validate_comparable_metrics(tree, forest)

    def test_macro_recall_excludes_null_recall(self):
        metrics = sample_metrics()
        metrics["support"]["7"] = 0
        metrics["recall"]["7"] = None

        self.assertAlmostEqual(macro_recall(metrics), 0.3)

    def test_rejects_missing_required_field_with_specific_message(self):
        forest = sample_metrics()
        del forest["accuracy"]

        with self.assertRaisesRegex(ValueError, "random_forest missing required field: accuracy"):
            validate_comparable_metrics(sample_metrics(), forest)

    def test_pipeline_writes_exact_headers_and_values_and_preserves_output_on_invalid_input(self):
        tree = sample_metrics(accuracy=0.25)
        forest = sample_metrics(accuracy=0.75, recall_offset=0.1)
        tree["recall"]["7"] = None
        forest["recall"]["7"] = None
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tree_path = root / "tree.json"
            forest_path = root / "forest.json"
            output_path = root / "model_comparison.csv"
            tree_path.write_text(json.dumps(tree), encoding="utf-8")
            forest_path.write_text(json.dumps(forest), encoding="utf-8")

            run_pipeline(tree_path, forest_path, output_path)
            with output_path.open(encoding="utf-8", newline="") as source:
                reader = csv.DictReader(source)
                rows = list(reader)
                headers = reader.fieldnames

            self.assertEqual(
                headers,
                [
                    "model",
                    "accuracy",
                    "macro_recall",
                    "recall_0",
                    "support_0",
                    "recall_1",
                    "support_1",
                    "recall_2",
                    "support_2",
                    "recall_3",
                    "support_3",
                    "recall_4",
                    "support_4",
                    "recall_5",
                    "support_5",
                    "recall_6",
                    "support_6",
                    "recall_7",
                    "support_7",
                ],
            )
            for row, model_name, metrics in (
                (rows[0], "decision_tree", tree),
                (rows[1], "random_forest", forest),
            ):
                self.assertEqual(row["model"], model_name)
                self.assertEqual(row["accuracy"], str(metrics["accuracy"]))
                non_null_recalls = [
                    value for value in metrics["recall"].values() if value is not None
                ]
                expected_macro_recall = sum(non_null_recalls) / len(non_null_recalls)
                self.assertEqual(row["macro_recall"], str(expected_macro_recall))
                for label in range(8):
                    expected_recall = metrics["recall"][str(label)]
                    self.assertEqual(
                        row[f"recall_{label}"],
                        "" if expected_recall is None else str(expected_recall),
                    )
                    self.assertEqual(
                        row[f"support_{label}"], str(metrics["support"][str(label)])
                    )

            original_csv = output_path.read_text(encoding="utf-8")
            forest["support"]["7"] = 99
            forest_path.write_text(json.dumps(forest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "support"):
                run_pipeline(tree_path, forest_path, output_path)
            self.assertEqual(output_path.read_text(encoding="utf-8"), original_csv)

    def test_invalid_inputs_do_not_create_output_when_it_does_not_exist(self):
        tree = sample_metrics()
        forest = sample_metrics()
        forest["test_rows"] = 9
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tree_path = root / "tree.json"
            forest_path = root / "forest.json"
            output_path = root / "model_comparison.csv"
            tree_path.write_text(json.dumps(tree), encoding="utf-8")
            forest_path.write_text(json.dumps(forest), encoding="utf-8")

            self.assertFalse(output_path.exists())
            with self.assertRaisesRegex(ValueError, "test_rows"):
                run_pipeline(tree_path, forest_path, output_path)
            self.assertFalse(output_path.exists())

    def test_load_failure_identifies_metrics_path(self):
        missing = Path("missing-model-metrics.json")

        with self.assertRaisesRegex(ValueError, "missing-model-metrics.json"):
            load_metrics(missing)


if __name__ == "__main__":
    unittest.main()
