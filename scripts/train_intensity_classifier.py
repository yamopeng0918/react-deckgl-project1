import argparse
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
from sklearn.metrics import accuracy_score, confusion_matrix, recall_score
from sklearn.tree import DecisionTreeClassifier


REQUIRED_COLUMNS = {
    "event_time",
    "year",
    "longitude",
    "latitude",
    "magnitude",
    "depth_km",
    "max_intensity",
}

INTENSITY_ALIASES = {
    "5弱": 5,
    "5強": 5,
    "6弱": 6,
    "6強": 6,
}

LABELS = list(range(8))
CANDIDATE_PARAMETERS = [
    {"max_depth": depth, "min_samples_leaf": leaf}
    for depth in (4, 6, 8, 12, None)
    for leaf in (1, 5, 10, 25)
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

            rows.append(
                {"year": event_time.year, "features": features, "target": target}
            )

    summary["usable_rows"] = len(rows)
    return rows, summary


def split_rows(rows, train_end_year, test_start_year):
    if train_end_year >= test_start_year:
        raise ValueError("Training and test periods overlap")
    train_rows = [row for row in rows if row["year"] <= train_end_year]
    test_rows = [row for row in rows if row["year"] >= test_start_year]
    return train_rows, test_rows


def _features_and_targets(rows):
    return [row["features"] for row in rows], [row["target"] for row in rows]


def select_model(train_rows):
    if not train_rows:
        raise ValueError("No usable training rows")

    ordered_rows = sorted(
        train_rows,
        key=lambda row: (row["year"], row["features"], row["target"]),
    )
    validation_end_year = max(row["year"] for row in ordered_rows)
    validation_start_year = validation_end_year - 2
    fit_rows = [row for row in ordered_rows if row["year"] < validation_start_year]
    validation_rows = [
        row for row in ordered_rows if row["year"] >= validation_start_year
    ]
    if not fit_rows or not validation_rows:
        raise ValueError("Training data cannot form chronological validation periods")

    fit_x, fit_y = _features_and_targets(fit_rows)
    validation_x, validation_y = _features_and_targets(validation_rows)
    validation_labels = sorted(set(validation_y))
    candidates = []

    for parameters in CANDIDATE_PARAMETERS:
        model = DecisionTreeClassifier(
            **parameters,
            class_weight="balanced",
            random_state=42,
        )
        model.fit(fit_x, fit_y)
        predictions = model.predict(validation_x)
        macro_recall = recall_score(
            validation_y,
            predictions,
            labels=validation_labels,
            average="macro",
            zero_division=0,
        )
        accuracy = accuracy_score(validation_y, predictions)
        candidates.append((macro_recall, accuracy, parameters))

    best_recall, best_accuracy, best_parameters = max(
        candidates,
        key=lambda item: (
            item[0],
            item[1],
            -(item[2]["max_depth"] or 10_000),
            -item[2]["min_samples_leaf"],
        ),
    )
    final_model = DecisionTreeClassifier(
        **best_parameters,
        class_weight="balanced",
        random_state=42,
    )
    all_x, all_y = _features_and_targets(ordered_rows)
    final_model.fit(all_x, all_y)
    summary = {
        **best_parameters,
        "validation_start_year": validation_start_year,
        "validation_end_year": validation_end_year,
        "validation_macro_recall": float(best_recall),
        "validation_accuracy": float(best_accuracy),
    }
    return final_model, summary


def evaluate_model(model, test_rows):
    if not test_rows:
        raise ValueError("No usable test rows")
    test_x, actual = _features_and_targets(test_rows)
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


def _write_confusion_matrix_plot(path, metrics):
    matrix = np.asarray(metrics["confusion_matrix"])
    figure, axis = plt.subplots(figsize=(9, 7))
    image = axis.imshow(matrix, interpolation="nearest", cmap="Blues")
    figure.colorbar(image, ax=axis)
    axis.set(
        title="Decision Tree Maximum-Intensity Confusion Matrix",
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


def run_pipeline(input_path, output_dir, train_end_year=2023, test_start_year=2024):
    rows, loading_summary = load_model_rows(input_path)
    train_rows, test_rows = split_rows(rows, train_end_year, test_start_year)
    if not train_rows:
        raise ValueError("No usable training rows")
    if not test_rows:
        raise ValueError("No usable test rows")

    model, selection = select_model(train_rows)
    evaluation = evaluate_model(model, test_rows)
    metrics = {
        **evaluation,
        "periods": {
            "train": [min(row["year"] for row in train_rows), train_end_year],
            "test": [test_start_year, max(row["year"] for row in test_rows)],
        },
        "input_summary": loading_summary,
        "train_rows": len(train_rows),
        "test_rows": len(test_rows),
        "selected_parameters": selection,
        "feature_names": [
            "magnitude",
            "depth_km",
            "longitude",
            "latitude",
            "month",
            "hour",
        ],
    }

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "decision_tree_metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    _write_class_report(output_dir / "decision_tree_class_report.csv", metrics)
    _write_confusion_matrix_csv(
        output_dir / "decision_tree_confusion_matrix.csv", metrics
    )
    _write_confusion_matrix_plot(
        output_dir / "decision_tree_confusion_matrix.png", metrics
    )
    joblib.dump(model, output_dir / "decision_tree_model.joblib")
    return metrics


def main():
    parser = argparse.ArgumentParser(
        description="Train and evaluate the maximum-intensity decision tree"
    )
    parser.add_argument(
        "--input", default="data/processed/earthquakes.csv", type=Path
    )
    parser.add_argument("--output-dir", default="data/model", type=Path)
    parser.add_argument("--train-end-year", default=2023, type=int)
    parser.add_argument("--test-start-year", default=2024, type=int)
    arguments = parser.parse_args()

    metrics = run_pipeline(
        arguments.input,
        arguments.output_dir,
        arguments.train_end_year,
        arguments.test_start_year,
    )
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print(f"Selected parameters: {metrics['selected_parameters']}")
    print("Per-class recall:")
    for label in metrics["labels"]:
        recall = metrics["recall"][str(label)]
        recall_text = "N/A" if recall is None else f"{recall:.4f}"
        print(
            f"  Intensity {label}: {recall_text} "
            f"(support={metrics['support'][str(label)]})"
        )
    print(f"Artifacts: {arguments.output_dir}")


if __name__ == "__main__":
    main()
