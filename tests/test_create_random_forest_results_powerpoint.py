import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from PIL import Image
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE

from scripts.create_random_forest_results_powerpoint import (
    create_random_forest_results_powerpoint,
    load_and_validate_metrics,
)


def valid_metrics():
    support = [1, 289, 1278, 910, 538, 19, 4, 0]
    matrix = [[0] * 8 for _ in range(8)]
    for label, count in enumerate(support):
        matrix[label][label] = count
    return {
        "accuracy": 0.4389601843,
        "labels": list(range(8)),
        "support": {str(i): value for i, value in enumerate(support)},
        "recall": {str(i): value for i, value in enumerate([0.0, 0.1938, 0.4319, 0.3978, 0.6487, 0.6842, 0.5, None])},
        "confusion_matrix": matrix,
        "periods": {"train": [1995, 2023], "test": [2024, 2026]},
        "train_rows": 13617,
        "test_rows": 3039,
        "selected_parameters": {
            "n_estimators": 200,
            "max_depth": 12,
            "min_samples_leaf": 1,
            "max_features": "sqrt",
            "class_weight": "balanced_subsample",
            "random_state": 42,
            "validation_start_year": 2021,
            "validation_end_year": 2023,
            "validation_macro_recall": 0.4206,
            "validation_accuracy": 0.4583,
        },
    }


class RandomForestResultsPowerPointTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        self.metrics_path = self.root / "metrics.json"
        self.matrix_path = self.root / "matrix.png"
        self.output_path = self.root / "results.pptx"
        self.metrics_path.write_text(json.dumps(valid_metrics()), encoding="utf-8")
        Image.new("RGB", (1200, 900), "white").save(self.matrix_path)

    def tearDown(self):
        self.directory.cleanup()

    def test_creates_valid_two_slide_widescreen_deck(self):
        create_random_forest_results_powerpoint(
            self.metrics_path, self.matrix_path, self.output_path
        )

        with zipfile.ZipFile(self.output_path) as package:
            self.assertIsNone(package.testzip())
        deck = Presentation(self.output_path)
        self.assertEqual(len(deck.slides), 2)
        self.assertAlmostEqual(deck.slide_width / deck.slide_height, 16 / 9, places=2)
        text = "\n".join(
            shape.text
            for slide in deck.slides
            for shape in slide.shapes
            if hasattr(shape, "text")
        )
        for expected in (
            "隨機森林最大震度分類結果",
            "Accuracy",
            "Macro Recall",
            "1995–2023",
            "2024–2026",
            "13,617",
            "3,039",
            "n_estimators=200",
            "max_features=sqrt",
            "強度 7：N/A（support 0）",
            "稀有類別",
            "分類，不是地震預測",
            "混淆矩陣",
            "實際類別（縱軸）",
            "預測類別（橫軸）",
            "2–4 級相鄰混淆",
            "0、6、7 級",
        ):
            self.assertIn(expected, text)

        pictures = [
            shape for shape in deck.slides[1].shapes
            if shape.shape_type == MSO_SHAPE_TYPE.PICTURE
        ]
        self.assertEqual(len(pictures), 1)
        picture = pictures[0]
        self.assertGreater(picture.width, deck.slide_width * 0.45)
        self.assertGreater(picture.height, deck.slide_height * 0.55)
        self.assertGreaterEqual(picture.left, 0)
        self.assertGreaterEqual(picture.top, 0)
        self.assertLessEqual(picture.left + picture.width, deck.slide_width)
        self.assertLessEqual(picture.top + picture.height, deck.slide_height)

    def _write_metrics(self, metrics):
        self.metrics_path.write_text(json.dumps(metrics), encoding="utf-8")

    def test_rejects_labels_other_than_exactly_zero_through_seven(self):
        metrics = valid_metrics()
        metrics["labels"] = list(range(7))
        self._write_metrics(metrics)

        with self.assertRaisesRegex(ValueError, "labels.*0.*7"):
            load_and_validate_metrics(self.metrics_path)

    def test_rejects_confusion_matrix_that_is_not_eight_by_eight(self):
        metrics = valid_metrics()
        metrics["confusion_matrix"] = [[0] * 8 for _ in range(7)]
        self._write_metrics(metrics)

        with self.assertRaisesRegex(ValueError, "confusion matrix.*8.*8"):
            load_and_validate_metrics(self.metrics_path)

    def test_rejects_matrix_row_total_that_disagrees_with_support(self):
        metrics = valid_metrics()
        metrics["confusion_matrix"][2][2] -= 1
        self._write_metrics(metrics)

        with self.assertRaisesRegex(ValueError, "row 2.*support"):
            load_and_validate_metrics(self.metrics_path)

    def test_rejects_missing_png_before_altering_output(self):
        self.output_path.write_bytes(b"existing")
        self.matrix_path.unlink()

        with self.assertRaisesRegex(FileNotFoundError, "confusion matrix PNG"):
            create_random_forest_results_powerpoint(
                self.metrics_path, self.matrix_path, self.output_path
            )

        self.assertEqual(self.output_path.read_bytes(), b"existing")

    def test_save_failure_preserves_existing_output_and_removes_temporary_file(self):
        self.output_path.write_bytes(b"existing deck")

        class FailingDeck:
            def save(self, _path):
                raise OSError("simulated save failure")

        with patch(
            "scripts.create_random_forest_results_powerpoint._build_deck",
            return_value=FailingDeck(),
        ):
            with self.assertRaisesRegex(OSError, "simulated save failure"):
                create_random_forest_results_powerpoint(
                    self.metrics_path, self.matrix_path, self.output_path
                )

        self.assertEqual(self.output_path.read_bytes(), b"existing deck")
        self.assertEqual(list(self.root.glob(".results-*.pptx")), [])


if __name__ == "__main__":
    unittest.main()
