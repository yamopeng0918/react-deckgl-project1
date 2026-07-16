# Random Forest Results PowerPoint Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate a reproducible two-slide 16:9 PowerPoint containing random-forest accuracy, macro recall, per-intensity recall/support, and a large confusion matrix.

**Architecture:** Add an independent python-pptx generator that validates the existing random-forest metrics and matrix PNG before writing to a temporary PPTX and atomically replacing the destination. Keep the existing two-model comparison generator unchanged.

**Tech Stack:** Python 3, python-pptx, Pillow, unittest, ZIP/OpenXML

## Global Constraints

- Default inputs are `data/model/random_forest_metrics.json` and `data/model/random_forest_confusion_matrix.png`.
- Default output is `data/model/random-forest-results.pptx`.
- Output is exactly two 16:9 slides.
- Slide 1 contains Accuracy, Macro Recall, train/test periods and counts, selected parameters, intensity 0–7 recall/support, rare-class caveat, and a classification-not-forecasting statement.
- Slide 2 embeds the full confusion-matrix PNG without cropping and includes actual/predicted axis guidance plus honest observations.
- Reject labels other than exactly 0–7, non-8×8 matrices, support/matrix disagreements, or missing inputs before replacing an existing output.
- Preserve the existing decision-tree/random-forest comparison PowerPoint and generator.

---

### Task 1: Build the Validated Two-Slide Generator

**Files:**
- Create: `scripts/create_random_forest_results_powerpoint.py`
- Create: `tests/test_create_random_forest_results_powerpoint.py`

**Interfaces:**
- Produce `load_and_validate_metrics(metrics_path)`, `create_random_forest_results_powerpoint(metrics_path, matrix_path, output_path)`, and `main()`.

- [ ] **Step 1: Write failing structure/content tests**

Create temporary valid metrics JSON and a small PNG fixture. Call the not-yet-existing generator and assert the PPTX has exactly two slides, 16:9 dimensions, ZIP integrity, the required slide text, and one image relationship on slide 2.

- [ ] **Step 2: Run RED**

Run: `python -m unittest tests.test_create_random_forest_results_powerpoint -v`

Expected: import failure because the generator does not exist.

- [ ] **Step 3: Implement validation and slide creation**

Validate these invariants before writing:

```python
labels == list(range(8))
len(confusion_matrix) == 8
all(len(row) == 8 for row in confusion_matrix)
[sum(row) for row in confusion_matrix] == [support[str(i)] for i in range(8)]
```

Compute macro recall as the mean of non-null recalls declared by labels. Create a `Presentation`, set `slide_width = Inches(13.333333)` and `slide_height = Inches(7.5)`, and build the approved two-slide layout using the existing model-report palette and `Microsoft JhengHei`.

Use `slide.shapes.add_picture()` with contained-fit dimensions so the matrix PNG is not cropped. Write the PPTX to a uniquely named temporary sibling, validate it can be opened, then `os.replace()` the final output. Clean temporary files on failure.

- [ ] **Step 4: Add failing invalid-input/output-preservation tests**

Test malformed labels, non-8×8 matrix, support mismatch, missing PNG, and a simulated save failure. Each must raise a clear error and preserve an existing output byte-for-byte.

- [ ] **Step 5: Run GREEN**

Run: `python -m unittest tests.test_create_random_forest_results_powerpoint -v`

Expected: all focused tests pass with pristine output.

- [ ] **Step 6: Commit**

```powershell
git add scripts/create_random_forest_results_powerpoint.py tests/test_create_random_forest_results_powerpoint.py
git commit -m "feat: add random forest results PowerPoint"
```

---

### Task 2: Generate and Verify the Real PowerPoint

**Files:**
- Generate: `data/model/random-forest-results.pptx`
- Modify: `README.md`
- Modify: `todo.md`
- Modify: `progress.md`

**Interfaces:**
- Consume the Task 1 CLI with default paths.
- Produce the real two-slide PowerPoint and project documentation.

- [ ] **Step 1: Add the PowerPoint checklist to todo**

Add tasks for generator, two-slide output, confusion-matrix embedding, structural validation, and documentation. Mark complete only after verification.

- [ ] **Step 2: Generate the real deck**

Run: `python scripts/create_random_forest_results_powerpoint.py`

Expected: exit 0 and `data/model/random-forest-results.pptx` exists.

- [ ] **Step 3: Independently verify the deck**

Open it with `zipfile.ZipFile` and `pptx.Presentation`; assert no bad ZIP entry, exactly two slides, 16:9 dimensions, required text on each slide, and a slide-2 image relationship. Verify the embedded media bytes equal the source PNG bytes.

- [ ] **Step 4: Update documentation**

Add the exact rerun command and output path to README. Record the measured accuracy 43.90%, macro recall 40.81%, per-class recall/support, output size/hash, and verification evidence in `progress.md`; complete the new `todo.md` section.

- [ ] **Step 5: Run complete verification**

Run:

```powershell
python -W error::ResourceWarning -m unittest discover -s tests -p 'test_*.py' -v
npm.cmd test -- --run
npm.cmd run build
```

Expected: Python and Vitest suites pass; build exits 0 with only the accepted deck.gl/MapLibre large-chunk warning.

- [ ] **Step 6: Review scope and commit**

Do not stage the pre-existing regenerated `data/model/decision-tree-results-review.pptx` modification unless it is intentionally restored to HEAD first without discarding user work. Stage only the new deck and documentation:

```powershell
git add README.md todo.md progress.md data/model/random-forest-results.pptx
git commit -m "docs: add random forest results deck"
```

