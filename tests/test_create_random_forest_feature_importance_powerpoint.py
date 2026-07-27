import math
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import joblib

from scripts.create_random_forest_feature_importance_powerpoint import (
    FEATURE_NAMES,
    build_insights,
    load_feature_importances,
    rank_feature_importances,
)


CURRENT_IMPORTANCES = (
    ("magnitude", 0.3113),
    ("depth_km", 0.1596),
    ("longitude", 0.1406),
    ("latitude", 0.2180),
    ("month", 0.0753),
    ("hour", 0.0952),
)


class FeatureImportanceExtractionTest(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.model_path = self.root / "model.joblib"

    def tearDown(self):
        self.temporary_directory.cleanup()

    def _write_model(self, **attributes):
        joblib.dump(SimpleNamespace(**attributes), self.model_path)

    def test_loads_the_six_feature_importances_in_model_feature_order(self):
        self._write_model(
            feature_importances_=[value for _, value in CURRENT_IMPORTANCES]
        )

        values = load_feature_importances(self.model_path)

        self.assertEqual(tuple(name for name, _ in values), FEATURE_NAMES)
        self.assertAlmostEqual(sum(value for _, value in values), 1.0)
        self.assertIsInstance(values, tuple)

    def test_rejects_a_missing_model_file(self):
        with self.assertRaisesRegex(FileNotFoundError, "model file not found"):
            load_feature_importances(self.model_path)

    def test_rejects_a_model_without_feature_importances(self):
        self._write_model()

        with self.assertRaisesRegex(ValueError, "feature_importances_"):
            load_feature_importances(self.model_path)

    def test_rejects_any_feature_count_other_than_six(self):
        self._write_model(feature_importances_=[0.2] * 5)

        with self.assertRaisesRegex(ValueError, "six feature importances"):
            load_feature_importances(self.model_path)

    def test_rejects_negative_or_non_finite_importances(self):
        for values in (
            [-0.01, 0.2, 0.2, 0.2, 0.2, 0.21],
            [math.nan, 0.2, 0.2, 0.2, 0.2, 0.2],
            [math.inf, 0.2, 0.2, 0.2, 0.2, 0.2],
        ):
            with self.subTest(values=values):
                self._write_model(feature_importances_=values)

                with self.assertRaisesRegex(ValueError, "finite non-negative"):
                    load_feature_importances(self.model_path)

    def test_rejects_importances_that_do_not_sum_to_one(self):
        self._write_model(feature_importances_=[0.1] * 6)

        with self.assertRaisesRegex(ValueError, "sum to one"):
            load_feature_importances(self.model_path)


class FeatureImportanceRankingTest(unittest.TestCase):
    def test_ranks_descending_and_preserves_feature_order_for_ties(self):
        values = (
            ("magnitude", 0.2),
            ("depth_km", 0.3),
            ("longitude", 0.3),
            ("latitude", 0.1),
            ("month", 0.05),
            ("hour", 0.05),
        )

        ranked = rank_feature_importances(values)

        self.assertEqual(
            ranked,
            (
                ("depth_km", 0.3),
                ("longitude", 0.3),
                ("magnitude", 0.2),
                ("latitude", 0.1),
                ("month", 0.05),
                ("hour", 0.05),
            ),
        )
        self.assertIsInstance(ranked, tuple)


class FeatureImportanceInsightTest(unittest.TestCase):
    def test_builds_current_model_insights_with_exact_percentages(self):
        insights = build_insights(CURRENT_IMPORTANCES)

        self.assertEqual(
            insights,
            (
                "規模是最重要的單一特徵（31.13%）",
                "經緯度合計 35.86%，顯示地理位置整體影響高於單一規模",
                "月份與時刻合計 17.05%，時間訊號存在，但不是主要依據",
            ),
        )
        self.assertIsInstance(insights, tuple)

    def test_uses_neutral_spatial_language_when_spatial_total_does_not_exceed_top_feature(self):
        insights = build_insights(
            (
                ("magnitude", 0.5),
                ("depth_km", 0.1),
                ("longitude", 0.1),
                ("latitude", 0.1),
                ("month", 0.1),
                ("hour", 0.1),
            )
        )

        self.assertNotIn("高於單一規模", insights[1])

    def test_uses_neutral_temporal_language_when_temporal_total_is_unusually_high(self):
        insights = build_insights(
            (
                ("magnitude", 0.25),
                ("depth_km", 0.1),
                ("longitude", 0.15),
                ("latitude", 0.1),
                ("month", 0.25),
                ("hour", 0.15),
            )
        )

        self.assertNotIn("不是主要依據", insights[2])


if __name__ == "__main__":
    unittest.main()
