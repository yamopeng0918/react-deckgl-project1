import argparse
import json
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt


NAVY = RGBColor(19, 35, 56)
INK = RGBColor(34, 43, 54)
MUTED = RGBColor(102, 114, 128)
PAPER = RGBColor(247, 245, 239)
WHITE = RGBColor(255, 255, 255)
TEAL = RGBColor(31, 128, 125)
AMBER = RGBColor(218, 147, 53)
PALE = RGBColor(226, 231, 230)
FONT = "Microsoft JhengHei"


def _set_text(shape, text, size, color=INK, bold=False, align=PP_ALIGN.LEFT):
    frame = shape.text_frame
    frame.clear()
    frame.margin_left = 0
    frame.margin_right = 0
    frame.margin_top = 0
    frame.margin_bottom = 0
    frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    paragraph = frame.paragraphs[0]
    paragraph.alignment = align
    run = paragraph.add_run()
    run.text = text
    run.font.name = FONT
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color


def _text_box(slide, x, y, w, h, text, size, **kwargs):
    shape = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    _set_text(shape, text, size, **kwargs)
    return shape


def _rounded_box(slide, x, y, w, h, fill, line=None, radius=True):
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
    shape = slide.shapes.add_shape(
        shape_type, Inches(x), Inches(y), Inches(w), Inches(h)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.color.rgb = line or fill
    return shape


def _add_metric_card(slide, x, y, w, label, value, note=None):
    card = _rounded_box(slide, x, y, w, 0.93, WHITE, PALE)
    _text_box(slide, x + 0.18, y + 0.10, w - 0.36, 0.22, label, 9, color=MUTED)
    _text_box(slide, x + 0.18, y + 0.31, w - 0.36, 0.34, value, 18, bold=True)
    if note:
        _text_box(slide, x + 0.18, y + 0.67, w - 0.36, 0.16, note, 7.5, color=MUTED)
    return card


def create_results_slide(metrics_path, matrix_path, output_path):
    metrics_path = Path(metrics_path)
    matrix_path = Path(matrix_path)
    output_path = Path(output_path)
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))

    deck = Presentation()
    deck.slide_width = Inches(13.333333)
    deck.slide_height = Inches(7.5)
    slide = deck.slides.add_slide(deck.slide_layouts[6])
    background = slide.background.fill
    background.solid()
    background.fore_color.rgb = PAPER

    _rounded_box(slide, 0, 0, 13.333, 0.16, TEAL, TEAL, radius=False)
    _text_box(
        slide,
        0.55,
        0.38,
        8.2,
        0.48,
        "台灣地震最大震度｜決策樹分類結果",
        24,
        color=NAVY,
        bold=True,
    )
    _text_box(
        slide,
        0.57,
        0.88,
        8.4,
        0.25,
        "時間外推驗證：以 1995–2023 訓練，2024–2026 測試",
        10.5,
        color=MUTED,
    )

    accuracy = metrics["accuracy"] * 100
    _add_metric_card(
        slide,
        0.55,
        1.35,
        1.75,
        "整體準確率",
        f"{accuracy:.2f}%",
        "chronological holdout",
    )
    _add_metric_card(
        slide,
        2.42,
        1.35,
        1.45,
        "訓練資料",
        f"{metrics['train_rows']:,}",
        "1995–2023",
    )
    _add_metric_card(
        slide,
        3.99,
        1.35,
        1.45,
        "測試資料",
        f"{metrics['test_rows']:,}",
        "2024–2026",
    )

    _text_box(slide, 0.57, 2.52, 4.6, 0.28, "各震度命中率（Recall）", 13, color=NAVY, bold=True)
    _text_box(slide, 0.57, 2.82, 4.6, 0.20, "百分比旁括號為測試樣本數", 8.5, color=MUTED)

    max_bar_width = 2.45
    for index, label in enumerate(metrics["labels"]):
        y = 3.10 + index * 0.39
        recall = metrics["recall"][str(label)]
        support = metrics["support"][str(label)]
        _text_box(slide, 0.58, y, 0.32, 0.22, str(label), 9.5, color=NAVY, bold=True)
        _rounded_box(slide, 0.96, y + 0.02, max_bar_width, 0.16, PALE, PALE, radius=False)
        if recall is not None and recall > 0:
            _rounded_box(
                slide,
                0.96,
                y + 0.02,
                max(0.04, max_bar_width * recall),
                0.16,
                TEAL if support >= 20 else AMBER,
                TEAL if support >= 20 else AMBER,
                radius=False,
            )
        value = "N/A" if recall is None else f"{recall * 100:.1f}%"
        _text_box(slide, 3.53, y - 0.01, 1.55, 0.24, f"{value}  ({support:,})", 8.5, color=INK)

    params = metrics["selected_parameters"]
    _text_box(
        slide,
        0.57,
        6.33,
        4.95,
        0.22,
        f"模型設定：max_depth={params['max_depth']} · min_samples_leaf={params['min_samples_leaf']}",
        8.5,
        color=MUTED,
    )

    matrix_card = _rounded_box(slide, 5.72, 1.35, 7.06, 5.20, WHITE, PALE)
    _text_box(slide, 5.98, 1.55, 4.0, 0.27, "混淆矩陣", 13, color=NAVY, bold=True)
    _text_box(slide, 9.78, 1.58, 2.68, 0.20, "列＝實際｜欄＝預測", 8.5, color=MUTED, align=PP_ALIGN.RIGHT)
    slide.shapes.add_picture(
        str(matrix_path), Inches(6.14), Inches(1.90), width=Inches(6.18), height=Inches(4.34)
    )

    footer = _rounded_box(slide, 0.55, 6.70, 12.23, 0.48, NAVY, NAVY)
    _text_box(
        slide,
        0.78,
        6.79,
        11.75,
        0.28,
        "結論｜目前為基準模型：整體辨識能力有限；震度 5、6 樣本僅 19、4 筆，震度 7 無測試樣本，命中率不宜視為穩定結論。",
        9.5,
        color=WHITE,
        bold=True,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    deck.save(output_path)
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Create a one-slide model-results deck")
    parser.add_argument(
        "--metrics", type=Path, default=Path("data/model/decision_tree_metrics.json")
    )
    parser.add_argument(
        "--matrix",
        type=Path,
        default=Path("data/model/decision_tree_confusion_matrix.png"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/model/decision-tree-results-review.pptx"),
    )
    arguments = parser.parse_args()
    output = create_results_slide(arguments.metrics, arguments.matrix, arguments.output)
    print(output)


if __name__ == "__main__":
    main()
