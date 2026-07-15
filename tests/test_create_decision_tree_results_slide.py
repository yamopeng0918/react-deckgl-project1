import tempfile
import unittest
from pathlib import Path

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE

from scripts.create_decision_tree_results_slide import create_results_slide


class DecisionTreeResultsSlideTest(unittest.TestCase):
    def test_creates_one_widescreen_slide_with_metrics_and_matrix(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "review.pptx"
            create_results_slide(
                root / "data/model/decision_tree_metrics.json",
                root / "data/model/decision_tree_confusion_matrix.png",
                output,
            )
            deck = Presentation(output)

        self.assertEqual(len(deck.slides), 1)
        self.assertAlmostEqual(deck.slide_width / deck.slide_height, 16 / 9, places=2)
        text = "\n".join(
            shape.text for shape in deck.slides[0].shapes if hasattr(shape, "text")
        )
        self.assertIn("28.33%", text)
        self.assertIn("1995–2023", text)
        self.assertIn("2024–2026", text)
        self.assertIn("基準模型", text)
        pictures = [
            shape
            for shape in deck.slides[0].shapes
            if shape.shape_type == MSO_SHAPE_TYPE.PICTURE
        ]
        self.assertGreaterEqual(len(pictures), 1)


if __name__ == "__main__":
    unittest.main()
