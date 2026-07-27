import math
from pathlib import Path

import joblib


FEATURE_NAMES = (
    "magnitude",
    "depth_km",
    "longitude",
    "latitude",
    "month",
    "hour",
)

FEATURE_LABELS = {
    "magnitude": "規模",
    "depth_km": "深度",
    "longitude": "經度",
    "latitude": "緯度",
    "month": "月份",
    "hour": "時刻",
}


def load_feature_importances(model_path) -> tuple[tuple[str, float], ...]:
    """Load and validate the fitted forest's six normalized importances."""
    model_path = Path(model_path)
    if not model_path.is_file():
        raise FileNotFoundError(f"model file not found: {model_path}")

    model = joblib.load(model_path)
    raw_importances = getattr(model, "feature_importances_", None)
    if raw_importances is None:
        raise ValueError("Model must expose feature_importances_")

    try:
        values = tuple(float(value) for value in raw_importances)
    except (TypeError, ValueError) as error:
        raise ValueError("feature importances must be finite non-negative numbers") from error

    if len(values) != len(FEATURE_NAMES):
        raise ValueError("Model must expose exactly six feature importances")
    if any(not math.isfinite(value) or value < 0 for value in values):
        raise ValueError("feature importances must be finite non-negative numbers")

    total = sum(values)
    if not math.isclose(total, 1.0, rel_tol=1e-6, abs_tol=1e-6):
        raise ValueError("feature importances must sum to one")

    return tuple(zip(FEATURE_NAMES, values))


def rank_feature_importances(importances) -> tuple[tuple[str, float], ...]:
    """Return importances from highest to lowest with stable feature-order ties."""
    feature_order = {name: index for index, name in enumerate(FEATURE_NAMES)}
    indexed_importances = tuple(importances)
    return tuple(
        sorted(
            indexed_importances,
            key=lambda item: (-item[1], feature_order.get(item[0], len(feature_order))),
        )
    )


def build_insights(importances) -> tuple[str, str, str]:
    """Build model-derived summary copy that remains accurate as values change."""
    values = dict(importances)
    top_name, top_value = rank_feature_importances(importances)[0]
    top_label = FEATURE_LABELS[top_name]
    spatial_total = values["longitude"] + values["latitude"]
    temporal_total = values["month"] + values["hour"]

    if spatial_total > top_value:
        spatial_comparison_text = (
            f"經緯度合計 {spatial_total:.2%}，顯示地理位置整體影響高於單一規模"
        )
    else:
        spatial_comparison_text = (
            f"經緯度合計 {spatial_total:.2%}，地理位置的相對影響應與其他特徵一併解讀"
        )

    magnitude_value = values["magnitude"]
    if temporal_total <= magnitude_value and temporal_total <= spatial_total:
        temporal_comparison_text = (
            f"月份與時刻合計 {temporal_total:.2%}，時間訊號存在，但不是主要依據"
        )
    else:
        temporal_comparison_text = (
            f"月份與時刻合計 {temporal_total:.2%}，時間訊號的相對影響應與其他特徵一併解讀"
        )

    return (
        f"{top_label}是最重要的單一特徵（{top_value:.2%}）",
        spatial_comparison_text,
        temporal_comparison_text,
    )
