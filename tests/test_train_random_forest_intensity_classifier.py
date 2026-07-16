import csv
import json
import subprocess
import sys
import tempfile
import unittest
import warnings
from pathlib import Path

import joblib

from scripts.intensity_model_common import evaluate_model, load_model_rows, split_rows

from scripts.train_random_forest_intensity_classifier import (
    CANDIDATE_PARAMETERS,
    selection_rank_key,
    run_pipeline,
    select_model,
)


class DirectCliExecutionTest(unittest.TestCase):
    def test_help_works_when_script_is_executed_directly(self):
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            [
                sys.executable,
                "scripts/train_random_forest_intensity_classifier.py",
                "--help",
            ],
            cwd=root,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--train-end-year", result.stdout)


def selection_rows():
    rows = []
    for year in range(2018, 2024):
        for label in range(4):
            rows.append(
                {
                    "year": year,
                    "features": [
                        3.0 + label,
                        8.0 + label,
                        120.5 + label / 10,
                        22.5 + label / 10,
                        float(label + 1),
                        float(label * 3),
                    ],
                    "target": label,
                }
            )
    return rows


class RandomForestSelectionTest(unittest.TestCase):
    def test_forced_tie_prefers_fewer_trees_shallower_finite_depth_and_larger_leaf(self):
        tied = [
            (0.5, 0.6, {"n_estimators": 500, "max_depth": None, "min_samples_leaf": 1}),
            (0.5, 0.6, {"n_estimators": 200, "max_depth": None, "min_samples_leaf": 5}),
            (0.5, 0.6, {"n_estimators": 200, "max_depth": 20, "min_samples_leaf": 5}),
            (0.5, 0.6, {"n_estimators": 200, "max_depth": 12, "min_samples_leaf": 3}),
            (0.5, 0.6, {"n_estimators": 200, "max_depth": 12, "min_samples_leaf": 5}),
        ]

        winner = max(tied, key=selection_rank_key)

        self.assertEqual(
            winner[2],
            {"n_estimators": 200, "max_depth": 12, "min_samples_leaf": 5},
        )

    def test_candidate_grid_contains_exactly_the_approved_parameters(self):
        expected = [
            {
                "n_estimators": trees,
                "max_depth": depth,
                "min_samples_leaf": leaf,
                "max_features": "sqrt",
                "class_weight": "balanced_subsample",
                "random_state": 42,
                "n_jobs": -1,
            }
            for trees in (200, 500)
            for depth in (12, 20, None)
            for leaf in (1, 3, 5)
        ]

        self.assertEqual(CANDIDATE_PARAMETERS, expected)
        self.assertEqual(len(CANDIDATE_PARAMETERS), 18)

    def test_selection_is_deterministic_and_uses_final_three_training_years(self):
        rows = selection_rows()

        first_model, first_summary = select_model(rows)
        reversed_model, reversed_summary = select_model(list(reversed(rows)))

        self.assertEqual(first_summary, reversed_summary)
        self.assertEqual(first_model.predict([row["features"] for row in rows]).tolist(),
                         reversed_model.predict([row["features"] for row in rows]).tolist())
        self.assertEqual(first_summary["validation_start_year"], 2021)
        self.assertEqual(first_summary["validation_end_year"], 2023)
        self.assertNotIn("n_jobs", first_summary)
        parameters = first_model.get_params()
        self.assertEqual(parameters["random_state"], 42)
        self.assertEqual(parameters["class_weight"], "balanced_subsample")
        self.assertEqual(parameters["max_features"], "sqrt")


class RandomForestPipelineArtifactTest(unittest.TestCase):
    def test_pipeline_creates_only_complete_reloadable_random_forest_artifacts(self):
        fieldnames = [
            "event_time", "year", "longitude", "latitude", "magnitude",
            "depth_km", "max_intensity",
        ]
        fixture_rows = []
        for year in range(2018, 2027):
            for label in range(8):
                fixture_rows.append(
                    {
                        "event_time": f"{year}-03-04T05:06:07",
                        "year": year,
                        "longitude": 120.5 + label / 10,
                        "latitude": 22.5 + label / 10,
                        "magnitude": 3.0 + label / 2,
                        "depth_km": 8.0 + label,
                        "max_intensity": label,
                    }
                )

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "earthquakes.csv"
            with input_path.open("w", encoding="utf-8", newline="") as output:
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(fixture_rows)

            output_dir = root / "model"
            metrics = run_pipeline(input_path, output_dir)

            self.assertEqual(
                {path.name for path in output_dir.iterdir()},
                {
                    "random_forest_metrics.json",
                    "random_forest_class_report.csv",
                    "random_forest_confusion_matrix.csv",
                    "random_forest_confusion_matrix.png",
                    "random_forest_model.joblib",
                },
            )
            saved_metrics = json.loads(
                (output_dir / "random_forest_metrics.json").read_text(encoding="utf-8")
            )
            png_header = (output_dir / "random_forest_confusion_matrix.png").read_bytes()[:8]
            with (output_dir / "random_forest_confusion_matrix.csv").open(
                encoding="utf-8", newline=""
            ) as matrix_file:
                matrix_rows = list(csv.reader(matrix_file))
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore",
                    message="Setting the shape on a NumPy array has been deprecated.*",
                    category=DeprecationWarning,
                )
                restored_model = joblib.load(output_dir / "random_forest_model.joblib")
            loaded_rows, _ = load_model_rows(input_path)
            _, test_rows = split_rows(loaded_rows, 2023, 2024)
            restored_metrics = evaluate_model(restored_model, test_rows)

        self.assertEqual(saved_metrics["model_type"], "random_forest")
        self.assertEqual(saved_metrics["labels"], list(range(8)))
        self.assertEqual(saved_metrics["periods"]["train"], [2018, 2023])
        self.assertEqual(saved_metrics["periods"]["test"], [2024, 2026])
        self.assertEqual(matrix_rows[0], ["actual\\predicted", *map(str, range(8))])
        self.assertEqual([row[0] for row in matrix_rows[1:]], list(map(str, range(8))))
        self.assertEqual(png_header, b"\x89PNG\r\n\x1a\n")
        self.assertEqual(restored_metrics["confusion_matrix"], metrics["confusion_matrix"])
        self.assertEqual(restored_metrics["support"], metrics["support"])


if __name__ == "__main__":
    unittest.main()
