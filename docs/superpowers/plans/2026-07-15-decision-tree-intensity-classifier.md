# Decision Tree Maximum-Intensity Classifier Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Train and evaluate a reproducible decision-tree classifier that predicts normalized Taiwan earthquake maximum intensity from the current processed dataset.

**Architecture:** A focused Python module owns normalization, feature extraction, chronological splitting, model selection, evaluation, and artifact writing. A thin CLI calls that module against `data/processed/earthquakes.csv`; unit and end-to-end tests use temporary fixture datasets so metric definitions and output formats are independently verifiable.

**Tech Stack:** Python 3, standard library, scikit-learn, joblib, matplotlib, unittest

## Global Constraints

- Normalize `5弱` and `5強` to class `5`, and `6弱` and `6強` to class `6`.
- Train on 1995–2023 and test only on 2024–2026.
- Features are magnitude, depth, longitude, latitude, month, and hour.
- Report accuracy, per-class recall, support, and an actual-row/predicted-column confusion matrix for labels `0–7`.
- Do not modify the frontend or overwrite source CSV files.

---

### Task 1: Dataset normalization and chronological split

**Files:**
- Create: `scripts/train_intensity_classifier.py`
- Create: `tests/test_train_intensity_classifier.py`
- Create: `requirements-model.txt`

**Interfaces:**
- Produces: `normalize_intensity(value) -> int | None`, `load_model_rows(path) -> tuple[list[dict], dict]`, and `split_rows(rows, train_end_year, test_start_year) -> tuple[list[dict], list[dict]]`.

- [ ] Write failing tests for legacy/new intensity labels, invalid targets, month/hour extraction, required columns, and chronological separation.
- [ ] Run `python -m unittest tests.test_train_intensity_classifier -v` and confirm failures precede implementation.
- [ ] Implement the minimum parsing and split functions, with exclusion counters for invalid targets/features.
- [ ] Add pinned-compatible model dependencies to `requirements-model.txt`.
- [ ] Re-run `python -m unittest tests.test_train_intensity_classifier -v` and confirm Task 1 tests pass.

### Task 2: Chronological model selection and metrics

**Files:**
- Modify: `scripts/train_intensity_classifier.py`
- Modify: `tests/test_train_intensity_classifier.py`

**Interfaces:**
- Consumes: normalized row dictionaries from Task 1.
- Produces: `select_model(train_rows) -> tuple[DecisionTreeClassifier, dict]` and `evaluate_model(model, test_rows) -> dict`.

- [ ] Write failing tests proving validation is contained within pre-2024 training data, parameter selection is deterministic, absent-class recall is `None`, and the confusion matrix uses actual rows and predicted columns.
- [ ] Run the focused unittest module and confirm the new assertions fail.
- [ ] Implement chronological validation over candidate `max_depth` and `min_samples_leaf` settings, selecting macro recall then accuracy with a deterministic tie-break.
- [ ] Implement accuracy, support, per-class recall, and the fixed-label `0–7` confusion matrix.
- [ ] Re-run the focused unittest module and confirm all Task 2 tests pass.

### Task 3: Artifacts and command-line execution

**Files:**
- Modify: `scripts/train_intensity_classifier.py`
- Modify: `tests/test_train_intensity_classifier.py`
- Modify: `.gitignore`

**Interfaces:**
- Consumes: selected fitted model and evaluation dictionary.
- Produces: `data/model/decision_tree_metrics.json`, `decision_tree_class_report.csv`, `decision_tree_confusion_matrix.csv`, `decision_tree_confusion_matrix.png`, and `decision_tree_model.joblib`.

- [ ] Write a failing end-to-end fixture test requiring all five artifacts and validating their key schema, labels, and matrix orientation.
- [ ] Run the focused unittest module and confirm the artifact test fails.
- [ ] Implement artifact writers, a headless matplotlib confusion-matrix plot, and an argparse CLI with configurable input/output and fixed default periods.
- [ ] Ignore the binary joblib artifact while retaining report files for review.
- [ ] Re-run the focused unittest module and confirm all tests pass.

### Task 4: Current-data run and project documentation

**Files:**
- Modify: `README.md`
- Modify: `progress.md`
- Modify: `todo.md`
- Generate: `data/model/decision_tree_metrics.json`
- Generate: `data/model/decision_tree_class_report.csv`
- Generate: `data/model/decision_tree_confusion_matrix.csv`
- Generate: `data/model/decision_tree_confusion_matrix.png`
- Generate and ignore: `data/model/decision_tree_model.joblib`

**Interfaces:**
- Consumes: current `data/processed/earthquakes.csv`.
- Produces: measured model results and rerun documentation.

- [ ] Install `requirements-model.txt` if dependencies are missing.
- [ ] Run `python scripts/train_intensity_classifier.py` on the current dataset and capture the actual selected parameters and metrics.
- [ ] Inspect JSON/CSV/PNG outputs for consistent labels, supports, totals, and dimensions.
- [ ] Update README with setup and rerun instructions, `todo.md` with completed model tasks, and `progress.md` with actual results and rare-class limitations.
- [ ] Run `python -m unittest tests.test_process_earthquakes tests.test_train_intensity_classifier -v`.
- [ ] Run `npm.cmd test -- --run` and `npm.cmd run build` to verify the existing application remains intact.
- [ ] Run `git diff --check` and inspect `git status --short` before reporting completion.
