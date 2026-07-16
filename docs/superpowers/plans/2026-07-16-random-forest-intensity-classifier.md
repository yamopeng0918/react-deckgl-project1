# Random Forest Maximum-Intensity Classifier Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a reproducible random-forest maximum-intensity classifier and a fair comparison with the existing decision tree without changing the established chronological evaluation design.

**Architecture:** Move model-independent loading, splitting, evaluation, and artifact-writing behavior into `scripts/intensity_model_common.py`, while retaining the decision-tree script as a compatible entry point. Add an independent random-forest trainer and a comparison generator that validates both metrics files before producing shared reporting artifacts.

**Tech Stack:** Python 3, scikit-learn, joblib, matplotlib, python-pptx, unittest

## Global Constraints

- Use `data/processed/earthquakes.csv` as the shared model input.
- Use magnitude, depth_km, longitude, latitude, event month, and event hour as the only features.
- Train on 1995–2023 and test only on 2024–2026.
- Select random-forest parameters with 2021–2023 validation macro recall; break ties by validation accuracy and then model simplicity.
- Use `random_state=42`, `max_features="sqrt"`, and `class_weight="balanced_subsample"` for every random-forest candidate.
- Preserve all existing decision-tree public functions, commands, and artifact filenames.
- Do not overwrite decision-tree artifacts when random-forest training fails.
- Report actual measured results and retain the rare-class limitation.

---

### Task 1: Extract the Shared Intensity-Model Core

**Files:**
- Create: `scripts/intensity_model_common.py`
- Modify: `scripts/train_intensity_classifier.py`
- Modify: `tests/test_train_intensity_classifier.py`

**Interfaces:**
- Produces: `LABELS`, `FEATURE_NAMES`, `normalize_intensity(value)`, `load_model_rows(path)`, `split_rows(rows, train_end_year, test_start_year)`, `features_and_targets(rows)`, `evaluate_model(model, test_rows)`, and `write_model_artifacts(model, metrics, output_dir, artifact_prefix, plot_title)`.
- Preserves: imports of `normalize_intensity`, `load_model_rows`, `split_rows`, and `evaluate_model` from `scripts.train_intensity_classifier`.

- [ ] **Step 1: Write a failing shared-core compatibility test**

Add to `tests/test_train_intensity_classifier.py`:

```python
from scripts import intensity_model_common


class SharedModelCoreTest(unittest.TestCase):
    def test_decision_tree_reexports_shared_core_functions(self):
        self.assertIs(normalize_intensity, intensity_model_common.normalize_intensity)
        self.assertIs(load_model_rows, intensity_model_common.load_model_rows)
        self.assertIs(split_rows, intensity_model_common.split_rows)
        self.assertIs(evaluate_model, intensity_model_common.evaluate_model)
        self.assertEqual(
            intensity_model_common.FEATURE_NAMES,
            ["magnitude", "depth_km", "longitude", "latitude", "month", "hour"],
        )
```

- [ ] **Step 2: Run the focused test and verify RED**

Run: `python -m unittest tests.test_train_intensity_classifier.SharedModelCoreTest -v`

Expected: FAIL because `scripts.intensity_model_common` does not exist.

- [ ] **Step 3: Move model-independent behavior into the shared module**

Create `scripts/intensity_model_common.py` with the existing constants and implementations for label normalization, CSV validation/loading, chronological splitting, stable row ordering, feature extraction, evaluation, and CSV/PNG/joblib output. Parameterize artifact names and the plot title:

```python
LABELS = list(range(8))
FEATURE_NAMES = [
    "magnitude", "depth_km", "longitude", "latitude", "month", "hour"
]


def stable_rows(rows):
    return sorted(rows, key=lambda row: (row["year"], row["features"], row["target"]))


def write_model_artifacts(
    model, metrics, output_dir, artifact_prefix, plot_title
):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / f"{artifact_prefix}_metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    write_class_report(output_dir / f"{artifact_prefix}_class_report.csv", metrics)
    write_confusion_matrix_csv(
        output_dir / f"{artifact_prefix}_confusion_matrix.csv", metrics
    )
    write_confusion_matrix_plot(
        output_dir / f"{artifact_prefix}_confusion_matrix.png", metrics, plot_title
    )
    joblib.dump(model, output_dir / f"{artifact_prefix}_model.joblib")
```

Update `scripts/train_intensity_classifier.py` to import and re-export the shared functions. Keep `CANDIDATE_PARAMETERS`, `select_model`, `run_pipeline`, and `main` in the decision-tree script. Replace its inline output calls with:

```python
write_model_artifacts(
    model,
    metrics,
    output_dir,
    artifact_prefix="decision_tree",
    plot_title="Decision Tree Maximum-Intensity Confusion Matrix",
)
```

- [ ] **Step 4: Run existing decision-tree tests and verify GREEN**

Run: `python -m unittest tests.test_train_intensity_classifier -v`

Expected: all existing and new tests PASS, including unchanged decision-tree artifact names and metrics.

- [ ] **Step 5: Commit the shared-core refactor**

```powershell
git add scripts/intensity_model_common.py scripts/train_intensity_classifier.py tests/test_train_intensity_classifier.py
git commit -m "refactor: share intensity model pipeline utilities"
```

---

### Task 2: Add Deterministic Random-Forest Selection and Artifacts

**Files:**
- Create: `scripts/train_random_forest_intensity_classifier.py`
- Create: `tests/test_train_random_forest_intensity_classifier.py`
- Modify: `.gitignore`

**Interfaces:**
- Consumes: shared-core functions from Task 1.
- Produces: `CANDIDATE_PARAMETERS`, `select_model(train_rows)`, `run_pipeline(input_path, output_dir, train_end_year=2023, test_start_year=2024)`, and five `random_forest_*` artifacts.

- [ ] **Step 1: Write failing tests for the parameter grid and deterministic selection**

Create `tests/test_train_random_forest_intensity_classifier.py` with fixture helpers reused or duplicated explicitly from the decision-tree test and these assertions:

```python
class RandomForestSelectionTest(unittest.TestCase):
    def test_candidate_grid_matches_approved_design(self):
        self.assertEqual(len(CANDIDATE_PARAMETERS), 18)
        self.assertEqual({p["n_estimators"] for p in CANDIDATE_PARAMETERS}, {200, 500})
        self.assertEqual({p["max_depth"] for p in CANDIDATE_PARAMETERS}, {12, 20, None})
        self.assertEqual({p["min_samples_leaf"] for p in CANDIDATE_PARAMETERS}, {1, 3, 5})

    def test_selection_is_deterministic_and_uses_2021_to_2023_validation(self):
        rows = make_balanced_rows(2018, 2023)
        first_model, first_summary = select_model(rows)
        second_model, second_summary = select_model(list(reversed(rows)))
        self.assertEqual(first_summary, second_summary)
        self.assertEqual(first_summary["validation_start_year"], 2021)
        self.assertEqual(first_summary["validation_end_year"], 2023)
        self.assertEqual(first_model.random_state, 42)
        self.assertEqual(first_model.class_weight, "balanced_subsample")
        self.assertEqual(first_model.max_features, "sqrt")
```

- [ ] **Step 2: Run selection tests and verify RED**

Run: `python -m unittest tests.test_train_random_forest_intensity_classifier.RandomForestSelectionTest -v`

Expected: FAIL because the random-forest trainer does not exist.

- [ ] **Step 3: Implement the approved grid and tie-breaking rule**

Create `scripts/train_random_forest_intensity_classifier.py`:

```python
CANDIDATE_PARAMETERS = [
    {
        "n_estimators": trees,
        "max_depth": depth,
        "min_samples_leaf": leaf,
        "max_features": "sqrt",
        "class_weight": "balanced_subsample",
        "random_state": 42,
        "n_jobs": -1,
    }
    for trees in (200, 500)
    for depth in (12, 20, None)
    for leaf in (1, 3, 5)
]


def _simplicity_key(parameters):
    depth = parameters["max_depth"] if parameters["max_depth"] is not None else 10_000
    return (-parameters["n_estimators"], -depth, parameters["min_samples_leaf"])
```

In `select_model`, call `stable_rows`, use the last three years as validation, evaluate candidates with validation-label macro recall and accuracy, rank with `(macro_recall, accuracy, *_simplicity_key(parameters))`, then refit the winner on all training rows. Exclude `n_jobs` from the serializable selected-parameter summary because it is an execution setting, not a selected model characteristic.

- [ ] **Step 4: Write a failing end-to-end artifact test**

Add:

```python
class RandomForestPipelineArtifactTest(unittest.TestCase):
    def test_pipeline_creates_reloadable_labeled_artifacts(self):
        metrics, output_dir = run_fixture_pipeline()
        self.assertEqual(
            {path.name for path in output_dir.iterdir()},
            {
                "random_forest_metrics.json",
                "random_forest_class_report.csv",
                "random_forest_confusion_matrix.csv",
                "random_forest_confusion_matrix.png",
                "random_forest_model.joblib",
            },
        )
        restored = joblib.load(output_dir / "random_forest_model.joblib")
        restored_metrics = evaluate_model(restored, fixture_test_rows())
        self.assertEqual(restored_metrics["confusion_matrix"], metrics["confusion_matrix"])
        self.assertEqual(restored_metrics["support"], metrics["support"])
```

- [ ] **Step 5: Run the artifact test and verify RED**

Run: `python -m unittest tests.test_train_random_forest_intensity_classifier.RandomForestPipelineArtifactTest -v`

Expected: FAIL because `run_pipeline` does not yet emit the required artifact set.

- [ ] **Step 6: Implement pipeline, CLI, and local model ignore rule**

Build metrics with the same keys as the decision tree, add `model_type: "random_forest"`, and write artifacts through:

```python
write_model_artifacts(
    model,
    metrics,
    output_dir,
    artifact_prefix="random_forest",
    plot_title="Random Forest Maximum-Intensity Confusion Matrix",
)
```

Add `.gitignore` entry:

```gitignore
data/model/random_forest_model.joblib
```

The CLI defaults must match the existing decision-tree command: input `data/processed/earthquakes.csv`, output `data/model`, train end 2023, test start 2024.

- [ ] **Step 7: Run both model test modules and verify GREEN**

Run: `python -m unittest tests.test_train_intensity_classifier tests.test_train_random_forest_intensity_classifier -v`

Expected: both modules PASS.

- [ ] **Step 8: Commit the random-forest pipeline**

```powershell
git add .gitignore scripts/train_random_forest_intensity_classifier.py tests/test_train_random_forest_intensity_classifier.py
git commit -m "feat: add random forest intensity classifier"
```

---

### Task 3: Generate and Validate the Two-Model Comparison

**Files:**
- Create: `scripts/compare_intensity_models.py`
- Create: `tests/test_compare_intensity_models.py`

**Interfaces:**
- Consumes: `decision_tree_metrics.json` and `random_forest_metrics.json`.
- Produces: `validate_comparable_metrics(tree_metrics, forest_metrics)`, `build_comparison_rows(...)`, and `model_comparison.csv`.

- [ ] **Step 1: Write failing validation and CSV tests**

Create `tests/test_compare_intensity_models.py`:

```python
class ComparableMetricsTest(unittest.TestCase):
    def test_rejects_different_test_support(self):
        tree, forest = matching_metrics()
        forest["support"]["6"] += 1
        with self.assertRaisesRegex(ValueError, "support"):
            validate_comparable_metrics(tree, forest)

    def test_writes_accuracy_macro_recall_and_all_class_metrics(self):
        tree, forest = matching_metrics()
        rows = build_comparison_rows(tree, forest)
        self.assertEqual([row["model"] for row in rows], ["decision_tree", "random_forest"])
        self.assertIn("macro_recall", rows[0])
        for label in range(8):
            self.assertIn(f"recall_{label}", rows[0])
            self.assertIn(f"support_{label}", rows[0])
```

- [ ] **Step 2: Run focused tests and verify RED**

Run: `python -m unittest tests.test_compare_intensity_models -v`

Expected: FAIL because the comparison module does not exist.

- [ ] **Step 3: Implement strict comparison validation and output**

Validate exact equality for `periods.test`, `test_rows`, `labels`, and `support`. Compute macro recall from non-null per-class recalls so it is explicitly traceable to metrics JSON:

```python
def macro_recall(metrics):
    values = [metrics["recall"][str(label)] for label in metrics["labels"]]
    usable = [value for value in values if value is not None]
    return sum(usable) / len(usable)


def build_comparison_rows(tree_metrics, forest_metrics):
    validate_comparable_metrics(tree_metrics, forest_metrics)
    rows = []
    for model_name, metrics in (
        ("decision_tree", tree_metrics),
        ("random_forest", forest_metrics),
    ):
        row = {
            "model": model_name,
            "accuracy": metrics["accuracy"],
            "macro_recall": macro_recall(metrics),
        }
        for label in metrics["labels"]:
            row[f"recall_{label}"] = metrics["recall"][str(label)]
            row[f"support_{label}"] = metrics["support"][str(label)]
        rows.append(row)
    return rows
```

Write `model_comparison.csv` atomically only after both JSON files load and validate.

- [ ] **Step 4: Run comparison and all model tests and verify GREEN**

Run: `python -m unittest tests.test_compare_intensity_models tests.test_train_intensity_classifier tests.test_train_random_forest_intensity_classifier -v`

Expected: all tests PASS.

- [ ] **Step 5: Commit the comparison generator**

```powershell
git add scripts/compare_intensity_models.py tests/test_compare_intensity_models.py
git commit -m "feat: compare intensity classification models"
```

---

### Task 4: Update the One-Page Results Deck and Closing Report Copy

**Files:**
- Modify: `scripts/create_decision_tree_results_slide.py`
- Modify: `tests/test_create_decision_tree_results_slide.py`
- Modify: `hyperframes/closing-report/index.html` (local-only file; do not Git-add)
- Modify: `tests/hyperframesClosingReport.test.js`
- Regenerate: `data/model/decision-tree-results-review.pptx`
- Regenerate locally: `hyperframes/closing-report/decision-tree-results.pptx`

**Interfaces:**
- Consumes: both metrics JSON files, both confusion-matrix PNG files, and `model_comparison.csv`.
- Produces: a one-slide two-model comparison deck and updated closing-report model text.

- [ ] **Step 1: Write failing PowerPoint content tests**

Extend `tests/test_create_decision_tree_results_slide.py` to call the generator with both model metrics and assert extracted slide XML contains:

```python
self.assertIn("決策樹", slide_text)
self.assertIn("隨機森林", slide_text)
self.assertIn("Accuracy", slide_text)
self.assertIn("Macro Recall", slide_text)
self.assertIn("稀有類別", slide_text)
```

Also assert both metrics values appear after formatting to two decimal places and the deck remains exactly one 16:9 slide.

- [ ] **Step 2: Run the PowerPoint test and verify RED**

Run: `python -m unittest tests.test_create_decision_tree_results_slide -v`

Expected: FAIL because the generator accepts and displays only decision-tree results.

- [ ] **Step 3: Implement the compact two-model slide**

Change `create_results_slide` to accept:

```python
def create_results_slide(
    decision_tree_metrics_path,
    random_forest_metrics_path,
    comparison_path,
    output_path,
):
```

Retain the existing visual system. Use two side-by-side metric columns, one shared chronological-period strip, one compact per-class recall/support table, and a bottom limitation note. Derive the comparison sentence from measured test macro recall first and accuracy second; if tied, state that neither model clearly leads.

- [ ] **Step 4: Write and verify the closing-report test RED state**

Update `tests/hyperframesClosingReport.test.js` so page 4 must contain both `決策樹` and `隨機森林`, plus the measured comparison conclusion. Run:

`npm.cmd test -- --run tests/hyperframesClosingReport.test.js`

Expected: FAIL because the local page still reports only the decision tree.

- [ ] **Step 5: Update only model-related closing-report copy**

Edit the local-only `hyperframes/closing-report/index.html` page 4 and page 5 text to mention both trained models, the common chronological evaluation, and the measured comparison. Keep scene count, timing, layout, and unrelated copy unchanged.

- [ ] **Step 6: Run focused report tests and verify GREEN**

Run:

```powershell
python -m unittest tests.test_create_decision_tree_results_slide -v
npm.cmd test -- --run tests/hyperframesClosingReport.test.js
```

Expected: both focused suites PASS.

- [ ] **Step 7: Commit tracked generator and test changes**

Do not add `hyperframes/closing-report/` because the directory is intentionally local-only.

```powershell
git add scripts/create_decision_tree_results_slide.py tests/test_create_decision_tree_results_slide.py tests/hyperframesClosingReport.test.js data/model/decision-tree-results-review.pptx
git commit -m "feat: compare models in results report"
```

---

### Task 5: Run Real Training, Document Results, and Complete Verification

**Files:**
- Modify: `README.md`
- Modify: `todo.md`
- Modify: `progress.md`
- Modify: `.gitignore` if the generated model needs a more exact ignore rule
- Regenerate: `data/model/decision_tree_*`
- Generate: `data/model/random_forest_*`
- Generate: `data/model/model_comparison.csv`

**Interfaces:**
- Consumes: all pipelines from Tasks 1–4 and the real processed dataset.
- Produces: verified real artifacts, rerun documentation, measured comparison, and final project records.

- [ ] **Step 1: Add pending random-forest tasks to `todo.md` before training**

Add a `Random-Forest Model Comparison` section with unchecked items for pipeline, chronological selection, artifacts, comparison, reporting, and verification. Do not mark them complete until their evidence exists.

- [ ] **Step 2: Run both real model pipelines and the comparison generator**

Run:

```powershell
python scripts/train_intensity_classifier.py
python scripts/train_random_forest_intensity_classifier.py
python scripts/compare_intensity_models.py
python scripts/create_decision_tree_results_slide.py
```

Expected: all commands exit 0 and produce both five-file model artifact sets, `model_comparison.csv`, and the updated one-page PPTX.

- [ ] **Step 3: Inspect generated metrics for comparability**

Run:

```powershell
python -c "import json; from pathlib import Path; p=Path('data/model'); a=json.loads((p/'decision_tree_metrics.json').read_text()); b=json.loads((p/'random_forest_metrics.json').read_text()); print(a['periods'], b['periods']); print(a['test_rows'], b['test_rows']); print(a['support']==b['support']); print(a['accuracy'], b['accuracy'])"
```

Expected: periods and test row counts match, support equality prints `True`, and both measured accuracies print.

- [ ] **Step 4: Update README and project records with measured values**

Document these exact rerun commands:

```powershell
python scripts/train_intensity_classifier.py
python scripts/train_random_forest_intensity_classifier.py
python scripts/compare_intensity_models.py
```

Explain the common six features, 1995–2023／2024–2026 split, 2021–2023 macro-recall parameter selection, artifact filenames, measured results, and rare-class limitation. Add a dated `progress.md` entry containing selected random-forest parameters, validation metrics, test accuracy, test macro recall, per-class recall/support, comparison conclusion, and verification evidence. Mark the new `todo.md` section complete only after all checks pass.

- [ ] **Step 5: Run the complete Python verification suite**

Run: `python -W error::ResourceWarning -m unittest discover -s tests -p 'test_*.py' -v`

Expected: all Python tests PASS with no ResourceWarning promoted to an error.

- [ ] **Step 6: Run frontend tests and production build**

Run:

```powershell
npm.cmd test -- --run
npm.cmd run build
```

Expected: all Vitest tests PASS; build exits 0. The existing deck.gl/MapLibre large-chunk warning is acceptable.

- [ ] **Step 7: Validate generated PowerPoint packages**

Run the existing PowerPoint tests plus ZIP integrity checks performed by those tests:

`python -m unittest tests.test_create_decision_tree_results_slide tests.test_create_closing_report_powerpoint -v`

Expected: tests PASS; the one-page result deck and closing-report deck inputs remain readable PowerPoint packages.

- [ ] **Step 8: Review Git scope and commit the completed model comparison**

Run `git status --short` and confirm no local-only closing-report files are staged. Then:

```powershell
git add .gitignore README.md todo.md progress.md data/model scripts tests
git commit -m "docs: record random forest model comparison"
```

Expected: commit succeeds; `git status --short` is clean except for intentionally ignored local-only artifacts.

