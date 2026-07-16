import csv
import json
import math
import os
import tempfile
from datetime import datetime
from pathlib import Path

import joblib

os.environ.setdefault(
    "MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "taiwan-earthquake-matplotlib")
)
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import accuracy_score, confusion_matrix


REQUIRED_COLUMNS = {
    "event_time",
    "year",
    "longitude",
    "latitude",
    "magnitude",
    "depth_km",
    "max_intensity",
}
INTENSITY_ALIASES = {"5弱": 5, "5強": 5, "6弱": 6, "6強": 6}
LABELS = list(range(8))
FEATURE_NAMES = [
    "magnitude",
    "depth_km",
    "longitude",
    "latitude",
    "month",
    "hour",
]


def normalize_intensity(value):
    if value is None:
        return None
    label = str(value).strip()
    if label in INTENSITY_ALIASES:
        return INTENSITY_ALIASES[label]
    try:
        numeric_value = float(label)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(numeric_value) or not numeric_value.is_integer():
        return None
    intensity = int(numeric_value)
    return intensity if 0 <= intensity <= 7 else None


def load_model_rows(path):
    path = Path(path)
    summary = {
        "input_rows": 0,
        "usable_rows": 0,
        "excluded_invalid_target": 0,
        "excluded_invalid_features": 0,
        "excluded_year_mismatch": 0,
    }
    rows = []
    with path.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        missing = sorted(REQUIRED_COLUMNS - set(reader.fieldnames or []))
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(missing)}")
        for source_row in reader:
            summary["input_rows"] += 1
            target = normalize_intensity(source_row["max_intensity"])
            if target is None:
                summary["excluded_invalid_target"] += 1
                continue
            try:
                event_time = datetime.fromisoformat(source_row["event_time"])
                year = int(source_row["year"])
                features = [
                    float(source_row["magnitude"]),
                    float(source_row["depth_km"]),
                    float(source_row["longitude"]),
                    float(source_row["latitude"]),
                    float(event_time.month),
                    float(event_time.hour),
                ]
            except (TypeError, ValueError):
                summary["excluded_invalid_features"] += 1
                continue
            if not all(math.isfinite(value) for value in features):
                summary["excluded_invalid_features"] += 1
                continue
            if year != event_time.year:
                summary["excluded_year_mismatch"] += 1
                continue
            rows.append({"year": event_time.year, "features": features, "target": target})
    summary["usable_rows"] = len(rows)
    return rows, summary


def split_rows(rows, train_end_year, test_start_year):
    if train_end_year >= test_start_year:
        raise ValueError("Training and test periods overlap")
    train_rows = [row for row in rows if row["year"] <= train_end_year]
    test_rows = [row for row in rows if row["year"] >= test_start_year]
    return train_rows, test_rows


def stable_rows(rows):
    return sorted(rows, key=lambda row: (row["year"], row["features"], row["target"]))


def features_and_targets(rows):
    return [row["features"] for row in rows], [row["target"] for row in rows]


def evaluate_model(model, test_rows):
    if not test_rows:
        raise ValueError("No usable test rows")
    test_x, actual = features_and_targets(test_rows)
    predicted = [int(value) for value in model.predict(test_x)]
    matrix = confusion_matrix(actual, predicted, labels=LABELS)
    support = {str(label): int(sum(matrix[label])) for label in LABELS}
    recall = {
        str(label): (
            float(matrix[label][label] / support[str(label)])
            if support[str(label)]
            else None
        )
        for label in LABELS
    }
    return {
        "accuracy": float(accuracy_score(actual, predicted)),
        "labels": LABELS,
        "support": support,
        "recall": recall,
        "confusion_matrix": matrix.astype(int).tolist(),
    }


def _write_class_report(path, metrics):
    with path.open("w", encoding="utf-8", newline="") as output:
        writer = csv.writer(output)
        writer.writerow(["intensity", "recall", "support"])
        for label in metrics["labels"]:
            writer.writerow(
                [label, metrics["recall"][str(label)], metrics["support"][str(label)]]
            )


def _write_confusion_matrix_csv(path, metrics):
    with path.open("w", encoding="utf-8", newline="") as output:
        writer = csv.writer(output)
        writer.writerow(["actual\\predicted", *metrics["labels"]])
        for label, row in zip(metrics["labels"], metrics["confusion_matrix"]):
            writer.writerow([label, *row])


def _write_confusion_matrix_plot(path, metrics, plot_title):
    matrix = np.asarray(metrics["confusion_matrix"])
    figure, axis = plt.subplots(figsize=(9, 7))
    image = axis.imshow(matrix, interpolation="nearest", cmap="Blues")
    figure.colorbar(image, ax=axis)
    axis.set(
        title=plot_title,
        xlabel="Predicted intensity",
        ylabel="Actual intensity",
        xticks=metrics["labels"],
        yticks=metrics["labels"],
    )
    threshold = matrix.max() / 2 if matrix.size else 0
    for actual_index in range(matrix.shape[0]):
        for predicted_index in range(matrix.shape[1]):
            value = int(matrix[actual_index, predicted_index])
            axis.text(
                predicted_index,
                actual_index,
                str(value),
                ha="center",
                va="center",
                color="white" if value > threshold else "black",
            )
    figure.tight_layout()
    figure.savefig(path, dpi=160)
    plt.close(figure)


def write_model_artifacts(model, metrics, output_dir, artifact_prefix, plot_title):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / f"{artifact_prefix}_metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    _write_class_report(output_dir / f"{artifact_prefix}_class_report.csv", metrics)
    _write_confusion_matrix_csv(
        output_dir / f"{artifact_prefix}_confusion_matrix.csv", metrics
    )
    _write_confusion_matrix_plot(
        output_dir / f"{artifact_prefix}_confusion_matrix.png", metrics, plot_title
    )
    joblib.dump(model, output_dir / f"{artifact_prefix}_model.joblib")
