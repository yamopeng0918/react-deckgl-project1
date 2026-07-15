# Decision Tree Maximum-Intensity Classifier Design

## Goal

Use the current processed Taiwan earthquake dataset to train a reproducible decision-tree classifier for normalized maximum intensity, then report overall accuracy, per-class recall, and a confusion matrix.

## Scope

- Input: `data/processed/earthquakes.csv`.
- Target: `max_intensity`.
- Model: scikit-learn `DecisionTreeClassifier`.
- Evaluation: chronological holdout, not a random train/test split.
- Deliverables: rerunnable Python code, automated tests, machine-readable metrics, a confusion-matrix CSV, and a confusion-matrix image.
- The frontend and deployed application are unchanged.

## Target Normalization

Normalize maximum intensity to integer classes `0` through `7`:

- `5弱` and `5強` become `5`.
- `6弱` and `6強` become `6`.
- Existing numeric values `0` through `7` remain unchanged.
- Rows with a missing or unsupported target are excluded and counted in the run summary.

This produces one consistent classification system across historical and recent source formats. Rare classes remain in the dataset and their limited support must be visible in the report.

## Features

Use only information available for an earthquake event:

- `magnitude`
- `depth_km`
- `longitude`
- `latitude`
- month derived from `event_time`
- hour derived from `event_time`

Exclude `id`, `location`, `source_file`, and the target itself. Do not use free-text location features in this MVP model.

Rows missing any required numeric feature or containing an invalid event timestamp are excluded and counted in the run summary.

## Chronological Evaluation

- Training period: 1995 through 2023.
- Test period: 2024 through 2026.
- No test record may be used for model selection.
- Select decision-tree hyperparameters using chronological validation contained entirely within the training period.
- Candidate settings cover tree depth and minimum leaf size. Selection prioritizes macro recall, with accuracy as the deterministic tie-breaker.
- Use a fixed random seed and deterministic ordering so repeated runs on unchanged input produce the same outputs.

## Outputs

Write generated artifacts under `data/model/`:

- `decision_tree_metrics.json`: periods, row counts, selected parameters, accuracy, class labels, per-class support, and per-class recall.
- `decision_tree_class_report.csv`: one row per normalized intensity class with recall and support.
- `decision_tree_confusion_matrix.csv`: labeled actual-by-predicted counts.
- `decision_tree_confusion_matrix.png`: presentation-ready visualization of the same matrix.
- `decision_tree_model.joblib`: fitted model artifact.

The command-line run prints the overall accuracy, selected parameters, per-class recall, and output paths.

## Metric Definitions

- Accuracy: correct test predictions divided by all test predictions.
- Per-class hit rate: recall for that actual class, `true positives / all actual examples of the class`.
- Confusion matrix: rows are actual classes and columns are predicted classes.
- Classes absent from the chronological test set remain listed with support `0` and recall `null` in JSON/CSV rather than being presented as a measured zero.

## Error Handling

Fail with a clear message when:

- the input file or required columns are missing;
- no usable training or test records remain;
- training or test periods overlap;
- model dependencies are unavailable;
- an output artifact cannot be written.

## Testing and Verification

Automated tests will cover:

- old and new intensity labels normalize correctly;
- missing and unsupported target values are excluded;
- feature extraction derives month and hour correctly;
- chronological splitting keeps 2024–2026 entirely out of training;
- reported recall and confusion-matrix orientation are correct on controlled fixtures;
- an end-to-end fixture run creates all required artifacts.

Final verification will run the complete model test suite, execute the model against the current processed dataset, inspect the generated metrics, and update `progress.md` and `todo.md` with the measured results and limitations.
