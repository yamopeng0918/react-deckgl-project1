import csv
import json
import tempfile
import unittest
import warnings
from pathlib import Path

import joblib

from scripts import intensity_model_common
import scripts.train_intensity_classifier as decision_tree
from scripts.train_intensity_classifier import (
    evaluate_model,
    load_model_rows,
    normalize_intensity,
    run_pipeline,
    select_model,
    split_rows,
)


class SharedModelCoreTest(unittest.TestCase):
    def test_decision_tree_reexports_shared_model_functions(self):
        for name in (
            "normalize_intensity",
            "load_model_rows",
            "split_rows",
            "evaluate_model",
        ):
            self.assertIs(getattr(decision_tree, name), getattr(intensity_model_common, name))

    def test_shared_feature_names_are_stable(self):
        self.assertEqual(
            intensity_model_common.FEATURE_NAMES,
            ["magnitude", "depth_km", "longitude", "latitude", "month", "hour"],
        )


FIELDNAMES = [
    "id",
    "event_time",
    "year",
    "longitude",
    "latitude",
    "magnitude",
    "depth_km",
    "max_intensity",
    "location",
    "source_file",
]


def earthquake_row(**overrides):
    row = {
        "id": "001",
        "event_time": "2023-03-04T05:06:07",
        "year": "2023",
        "longitude": "121.5",
        "latitude": "23.5",
        "magnitude": "5.2",
        "depth_km": "12.3",
        "max_intensity": "4",
        "location": "test",
        "source_file": "fixture.csv",
    }
    row.update(overrides)
    return row


class IntensityNormalizationTest(unittest.TestCase):
    def test_normalizes_legacy_and_modern_intensity_labels(self):
        expected = {
            "0": 0,
            "4": 4,
            "5": 5,
            "5弱": 5,
            "5強": 5,
            "6": 6,
            "6弱": 6,
            "6強": 6,
            "7": 7,
        }

        self.assertEqual(
            {label: normalize_intensity(label) for label in expected}, expected
        )

    def test_returns_none_for_missing_or_unsupported_intensity(self):
        for value in (None, "", "  ", "8", "unknown"):
            with self.subTest(value=value):
                self.assertIsNone(normalize_intensity(value))

    def test_accepts_integral_numeric_intensity_values(self):
        self.assertEqual(normalize_intensity(5.0), 5)
        self.assertEqual(normalize_intensity("6.0"), 6)
        self.assertIsNone(normalize_intensity(5.5))


class ModelRowLoadingTest(unittest.TestCase):
    def write_rows(self, directory, rows, fieldnames=FIELDNAMES):
        path = Path(directory) / "earthquakes.csv"
        with path.open("w", encoding="utf-8", newline="") as output:
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        return path

    def test_loads_numeric_features_and_derives_month_and_hour(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_rows(directory, [earthquake_row()])

            rows, summary = load_model_rows(path)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["features"], [5.2, 12.3, 121.5, 23.5, 3.0, 5.0])
        self.assertEqual(rows[0]["target"], 4)
        self.assertEqual(rows[0]["year"], 2023)
        self.assertEqual(summary["input_rows"], 1)
        self.assertEqual(summary["usable_rows"], 1)

    def test_counts_rows_excluded_for_invalid_target_or_feature(self):
        rows = [
            earthquake_row(id="001", max_intensity=""),
            earthquake_row(id="002", magnitude="not-a-number"),
            earthquake_row(id="003", event_time="invalid"),
            earthquake_row(id="004", depth_km="NaN"),
            earthquake_row(id="005", longitude="Infinity"),
            earthquake_row(id="006"),
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_rows(directory, rows)
            loaded, summary = load_model_rows(path)

        self.assertEqual(len(loaded), 1)
        self.assertEqual(summary["excluded_invalid_target"], 1)
        self.assertEqual(summary["excluded_invalid_features"], 4)

    def test_excludes_rows_when_year_disagrees_with_event_timestamp(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_rows(
                directory,
                [earthquake_row(year="2023", event_time="2024-01-01T00:00:00")],
            )

            loaded, summary = load_model_rows(path)

        self.assertEqual(loaded, [])
        self.assertEqual(summary["excluded_year_mismatch"], 1)

    def test_rejects_missing_required_columns(self):
        with tempfile.TemporaryDirectory() as directory:
            fieldnames = [name for name in FIELDNAMES if name != "depth_km"]
            path = self.write_rows(directory, [], fieldnames)

            with self.assertRaisesRegex(ValueError, "depth_km"):
                load_model_rows(path)


class ChronologicalSplitTest(unittest.TestCase):
    def test_keeps_2024_and_later_entirely_out_of_training(self):
        rows = [
            {"year": 1995},
            {"year": 2023},
            {"year": 2024},
            {"year": 2026},
        ]

        train_rows, test_rows = split_rows(rows, 2023, 2024)

        self.assertEqual([row["year"] for row in train_rows], [1995, 2023])
        self.assertEqual([row["year"] for row in test_rows], [2024, 2026])

    def test_rejects_overlapping_periods(self):
        with self.assertRaisesRegex(ValueError, "overlap"):
            split_rows([], 2024, 2024)


class StubModel:
    def __init__(self, predictions):
        self.predictions = predictions

    def predict(self, features):
        return self.predictions[: len(features)]


class ModelEvaluationTest(unittest.TestCase):
    def test_reports_fixed_labels_recall_support_and_matrix_orientation(self):
        test_rows = [
            {"year": 2024, "features": [1], "target": 1},
            {"year": 2024, "features": [2], "target": 1},
            {"year": 2025, "features": [3], "target": 2},
        ]

        metrics = evaluate_model(StubModel([1, 2, 2]), test_rows)

        self.assertAlmostEqual(metrics["accuracy"], 2 / 3)
        self.assertEqual(metrics["labels"], list(range(8)))
        self.assertEqual(metrics["support"]["1"], 2)
        self.assertEqual(metrics["recall"]["1"], 0.5)
        self.assertEqual(metrics["recall"]["2"], 1.0)
        self.assertIsNone(metrics["recall"]["7"])
        self.assertEqual(metrics["confusion_matrix"][1][2], 1)
        self.assertEqual(metrics["confusion_matrix"][2][2], 1)

    def test_model_selection_is_deterministic_and_uses_pre_2024_validation(self):
        train_rows = []
        for year in range(2018, 2024):
            for index in range(8):
                magnitude = 3.0 + index * 0.5
                train_rows.append(
                    {
                        "year": year,
                        "features": [magnitude, 10.0, 121.0, 23.5, 1.0, 0.0],
                        "target": min(7, index),
                    }
                )

        first_model, first_summary = select_model(train_rows)
        second_model, second_summary = select_model(list(reversed(train_rows)))

        self.assertEqual(first_summary, second_summary)
        self.assertLessEqual(first_summary["validation_end_year"], 2023)
        self.assertEqual(first_model.get_params()["random_state"], 42)
        self.assertEqual(
            first_model.get_params()["max_depth"], first_summary["max_depth"]
        )


class PipelineArtifactTest(unittest.TestCase):
    def test_end_to_end_run_creates_complete_labeled_artifacts(self):
        fixture_rows = []
        for year in range(2018, 2027):
            for index in range(16):
                fixture_rows.append(
                    earthquake_row(
                        id=f"{year}-{index}",
                        year=str(year),
                        event_time=f"{year}-03-04T05:06:07",
                        magnitude=str(3.0 + (index % 8) * 0.5),
                        max_intensity=str(index % 8),
                    )
                )

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "earthquakes.csv"
            with input_path.open("w", encoding="utf-8", newline="") as output:
                writer = csv.DictWriter(output, fieldnames=FIELDNAMES)
                writer.writeheader()
                writer.writerows(fixture_rows)

            output_dir = root / "model"
            metrics = run_pipeline(input_path, output_dir)

            expected_files = {
                "decision_tree_metrics.json",
                "decision_tree_class_report.csv",
                "decision_tree_confusion_matrix.csv",
                "decision_tree_confusion_matrix.png",
                "decision_tree_model.joblib",
            }
            self.assertEqual(
                {path.name for path in output_dir.iterdir()}, expected_files
            )
            saved_metrics = json.loads(
                (output_dir / "decision_tree_metrics.json").read_text(
                    encoding="utf-8"
                )
            )
            with (output_dir / "decision_tree_confusion_matrix.csv").open(
                encoding="utf-8", newline=""
            ) as matrix_file:
                matrix_rows = list(csv.reader(matrix_file))
            png_header = (output_dir / "decision_tree_confusion_matrix.png").read_bytes()[:8]
            loaded_rows, _ = load_model_rows(input_path)
            _, test_rows = split_rows(loaded_rows, 2023, 2024)
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore",
                    message="Setting the shape on a NumPy array has been deprecated.*",
                    category=DeprecationWarning,
                )
                restored_model = joblib.load(
                    output_dir / "decision_tree_model.joblib"
                )
            restored_metrics = evaluate_model(restored_model, test_rows)

        self.assertEqual(saved_metrics["labels"], list(range(8)))
        self.assertEqual(saved_metrics["periods"]["train"], [2018, 2023])
        self.assertEqual(saved_metrics["periods"]["test"], [2024, 2026])
        self.assertEqual(len(matrix_rows), 9)
        self.assertEqual(matrix_rows[0][0], "actual\\predicted")
        self.assertEqual(png_header, b"\x89PNG\r\n\x1a\n")
        self.assertEqual(metrics["test_rows"], 48)
        self.assertEqual(
            restored_metrics["confusion_matrix"], metrics["confusion_matrix"]
        )
        self.assertEqual(restored_metrics["support"], metrics["support"])


if __name__ == "__main__":
    unittest.main()
