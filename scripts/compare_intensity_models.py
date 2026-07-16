import argparse
import csv
import json
from pathlib import Path


REQUIRED_FIELDS = ("accuracy", "periods", "test_rows", "labels", "support", "recall")
FIELDNAMES = [
    "model",
    "accuracy",
    "macro_recall",
    *[
        column
        for label in range(8)
        for column in (f"recall_{label}", f"support_{label}")
    ],
]


def _require_fields(metrics, model_name):
    for field in REQUIRED_FIELDS:
        if field not in metrics:
            raise ValueError(f"{model_name} missing required field: {field}")
    if "test" not in metrics["periods"]:
        raise ValueError(f"{model_name} missing required field: periods.test")
    for field in ("support", "recall"):
        for label in range(8):
            if str(label) not in metrics[field]:
                raise ValueError(
                    f"{model_name} missing required field: {field}.{label}"
                )


def validate_comparable_metrics(tree_metrics, forest_metrics):
    _require_fields(tree_metrics, "decision_tree")
    _require_fields(forest_metrics, "random_forest")
    comparisons = {
        "periods.test": (
            tree_metrics["periods"]["test"],
            forest_metrics["periods"]["test"],
        ),
        "test_rows": (tree_metrics["test_rows"], forest_metrics["test_rows"]),
        "labels": (tree_metrics["labels"], forest_metrics["labels"]),
        "support": (tree_metrics["support"], forest_metrics["support"]),
    }
    for field, (tree_value, forest_value) in comparisons.items():
        if tree_value != forest_value:
            raise ValueError(f"Metrics mismatch: {field}")


def macro_recall(metrics):
    recalls = [value for value in metrics["recall"].values() if value is not None]
    if not recalls:
        raise ValueError("recall has no non-null values")
    return sum(recalls) / len(recalls)


def _comparison_row(model, metrics):
    row = {
        "model": model,
        "accuracy": metrics["accuracy"],
        "macro_recall": macro_recall(metrics),
    }
    for label in range(8):
        row[f"recall_{label}"] = metrics["recall"][str(label)]
        row[f"support_{label}"] = metrics["support"][str(label)]
    return row


def build_comparison_rows(tree_metrics, forest_metrics):
    validate_comparable_metrics(tree_metrics, forest_metrics)
    return [
        _comparison_row("decision_tree", tree_metrics),
        _comparison_row("random_forest", forest_metrics),
    ]


def load_metrics(path):
    path = Path(path)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Failed to load metrics from {path}: {error}") from error


def run_pipeline(tree_metrics_path, forest_metrics_path, output_path):
    tree_metrics = load_metrics(tree_metrics_path)
    forest_metrics = load_metrics(forest_metrics_path)
    rows = build_comparison_rows(tree_metrics, forest_metrics)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    return rows


def main():
    parser = argparse.ArgumentParser(description="Compare intensity classifiers")
    parser.add_argument(
        "--decision-tree-metrics",
        type=Path,
        default=Path("data/model/decision_tree_metrics.json"),
    )
    parser.add_argument(
        "--random-forest-metrics",
        type=Path,
        default=Path("data/model/random_forest_metrics.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/model/model_comparison.csv"),
    )
    arguments = parser.parse_args()
    run_pipeline(
        arguments.decision_tree_metrics,
        arguments.random_forest_metrics,
        arguments.output,
    )


if __name__ == "__main__":
    main()
