import argparse
from pathlib import Path

from sklearn.metrics import accuracy_score, recall_score
from sklearn.tree import DecisionTreeClassifier

if __package__:
    from scripts.intensity_model_common import (
        FEATURE_NAMES,
        LABELS,
        evaluate_model,
        features_and_targets,
        load_model_rows,
        normalize_intensity,
        split_rows,
        stable_rows,
        write_model_artifacts,
    )
else:
    from intensity_model_common import (
        FEATURE_NAMES,
        LABELS,
        evaluate_model,
        features_and_targets,
        load_model_rows,
        normalize_intensity,
        split_rows,
        stable_rows,
        write_model_artifacts,
    )


CANDIDATE_PARAMETERS = [
    {"max_depth": depth, "min_samples_leaf": leaf}
    for depth in (4, 6, 8, 12, None)
    for leaf in (1, 5, 10, 25)
]


def select_model(train_rows):
    if not train_rows:
        raise ValueError("No usable training rows")

    ordered_rows = stable_rows(train_rows)
    validation_end_year = max(row["year"] for row in ordered_rows)
    validation_start_year = validation_end_year - 2
    fit_rows = [row for row in ordered_rows if row["year"] < validation_start_year]
    validation_rows = [
        row for row in ordered_rows if row["year"] >= validation_start_year
    ]
    if not fit_rows or not validation_rows:
        raise ValueError("Training data cannot form chronological validation periods")

    fit_x, fit_y = features_and_targets(fit_rows)
    validation_x, validation_y = features_and_targets(validation_rows)
    validation_labels = sorted(set(validation_y))
    candidates = []
    for parameters in CANDIDATE_PARAMETERS:
        model = DecisionTreeClassifier(
            **parameters, class_weight="balanced", random_state=42
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
        **best_parameters, class_weight="balanced", random_state=42
    )
    all_x, all_y = features_and_targets(ordered_rows)
    final_model.fit(all_x, all_y)
    summary = {
        **best_parameters,
        "validation_start_year": validation_start_year,
        "validation_end_year": validation_end_year,
        "validation_macro_recall": float(best_recall),
        "validation_accuracy": float(best_accuracy),
    }
    return final_model, summary


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
        "feature_names": FEATURE_NAMES,
    }
    write_model_artifacts(
        model,
        metrics,
        output_dir,
        "decision_tree",
        "Decision Tree Maximum-Intensity Confusion Matrix",
    )
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
