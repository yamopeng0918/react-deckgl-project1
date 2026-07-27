# Random-Forest Feature-Importance Chart Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate a one-slide 16:9 PowerPoint with a real-model horizontal feature-importance chart and dynamically derived Traditional Chinese insights.

**Architecture:** A focused Python generator loads and validates the existing random-forest joblib, maps the six stable model features to audience-facing labels, derives ranked bars and aggregate insights, and draws them with native PowerPoint shapes. Tests verify model validation, ranking and insight semantics, chart geometry, East Asian typography, package integrity, and atomic output preservation.

**Tech Stack:** Python 3, scikit-learn, joblib, python-pptx, unittest, OpenXML ZIP inspection.

## Global Constraints

- Read values from `data/model/random_forest_model.joblib`; never hard-code feature importances.
- Include exactly six features: magnitude, depth, longitude, latitude, month, and hour.
- Use Traditional Chinese labels: 規模、深度、經度、緯度、月份、時刻.
- Generate insight comparisons from current values and never retain a conclusion contradicted by a future model.
- Produce exactly one 16:9 PowerPoint slide.
- Write Microsoft JhengHei to both Latin and East Asian DrawingML typefaces.
- Default output is `data/model/random-forest-feature-importance.pptx`.
- Do not overwrite existing result or three-level explainer decks.
- Preserve an existing output if generation or validation fails.

---

### Task 1: Model validation, ranking, and dynamic insights

**Files:**
- Create: `scripts/create_random_forest_feature_importance_powerpoint.py`
- Test: `tests/test_create_random_forest_feature_importance_powerpoint.py`

**Interfaces:**
- Consumes: fitted random-forest model loaded with joblib.
- Produces: `load_feature_importances(model_path) -> tuple[tuple[str, float], ...]`
- Produces: `rank_feature_importances(importances) -> tuple[tuple[str, float], ...]`
- Produces: `build_insights(importances) -> tuple[str, str, str]`

- [ ] **Step 1: Write failing extraction and validation tests**

Use small serializable fixtures and assert:

```python
values = load_feature_importances(model_path)
self.assertEqual(tuple(name for name, _ in values), FEATURE_NAMES)
self.assertAlmostEqual(sum(value for _, value in values), 1.0)
```

Add cases rejecting a missing file, missing `feature_importances_`, a length other than six, negative/non-finite values, and a total outside `math.isclose(total, 1.0, rel_tol=1e-6, abs_tol=1e-6)`.

- [ ] **Step 2: Run the focused test and verify RED**

```powershell
python -m unittest tests.test_create_random_forest_feature_importance_powerpoint -v
```

Expected: import failure because the generator module does not exist.

- [ ] **Step 3: Implement validated extraction and deterministic ranking**

Define:

```python
FEATURE_NAMES = ("magnitude", "depth_km", "longitude", "latitude", "month", "hour")
FEATURE_LABELS = {
    "magnitude": "規模",
    "depth_km": "深度",
    "longitude": "經度",
    "latitude": "緯度",
    "month": "月份",
    "hour": "時刻",
}
```

Return immutable tuples. Rank by descending importance and use original feature order as the deterministic tie-breaker.

- [ ] **Step 4: Write failing dynamic-insight tests**

For current-style values, assert exact percentages and the conclusion that spatial total exceeds the strongest individual feature. Add counterexamples where spatial total does not exceed the strongest feature and where temporal total is unusually high; assert that contradictory phrases such as `高於單一規模` or `不是主要依據` are absent.

- [ ] **Step 5: Implement insight derivation**

Produce:

```python
(
    f"{top_label}是最重要的單一特徵（{top_value:.2%}）",
    spatial_comparison_text,
    temporal_comparison_text,
)
```

Calculate spatial as longitude + latitude and temporal as month + hour. Use neutral language whenever the designed comparison is false.

- [ ] **Step 6: Run focused tests**

```powershell
python -m unittest tests.test_create_random_forest_feature_importance_powerpoint -v
```

Expected: extraction, validation, ranking, and insight tests pass.

- [ ] **Step 7: Commit Task 1**

```powershell
git add scripts/create_random_forest_feature_importance_powerpoint.py tests/test_create_random_forest_feature_importance_powerpoint.py
git commit -m "feat: derive random forest feature importance insights"
```

### Task 2: Native PowerPoint chart and real artifact

**Files:**
- Modify: `scripts/create_random_forest_feature_importance_powerpoint.py`
- Modify: `tests/test_create_random_forest_feature_importance_powerpoint.py`
- Create: `data/model/random-forest-feature-importance.pptx`

**Interfaces:**
- Consumes: validated ranked importance tuples and three dynamic insight strings.
- Produces: `build_deck(importances, insights) -> Presentation`
- Produces: `create_feature_importance_powerpoint(model_path, output_path) -> Path`

- [ ] **Step 1: Write failing deck-content and geometry tests**

Generate from a temporary six-feature model fixture and assert:

```python
self.assertEqual(len(deck.slides), 1)
self.assertAlmostEqual(deck.slide_width / deck.slide_height, 16 / 9, places=2)
for label in ("規模", "深度", "經度", "緯度", "月份", "時刻"):
    self.assertIn(label, slide_text)
```

Assert six identifiable bar shapes, descending display order, exact two-decimal percentage labels, shared zero baseline, widths proportional to values, all shapes inside slide bounds, and all visible text runs carrying both Latin and East Asian Microsoft JhengHei metadata.

- [ ] **Step 2: Run focused test and verify RED**

```powershell
python -m unittest tests.test_create_random_forest_feature_importance_powerpoint -v
```

Expected: failure because `build_deck` and the creation pipeline do not exist.

- [ ] **Step 3: Implement the one-slide native-shape chart**

Use a `13.333333 × 7.5` inch canvas:

- title/subtitle at the top;
- chart area from x=0.65 to x=8.75;
- six rows from y=1.55 through y=5.55;
- bar width `max_width * value / max_importance`;
- strongest feature in teal and remaining bars in progressively muted teal;
- three insight cards from x=9.15 to x=12.78;
- limitation line at the bottom.

Tag bar shape names as `importance-bar-<feature_name>` and node label shapes as `importance-label-<feature_name>` so tests can identify chart semantics without relying on shape order.

- [ ] **Step 4: Implement font metadata, atomic output, and CLI**

Set `run.font.name = "Microsoft JhengHei"` and write `a:ea typeface="Microsoft JhengHei"` for every visible run. Save to a temporary sibling file, validate ZIP integrity, exactly one slide, and 16:9 dimensions, then call `os.replace`.

CLI defaults:

```python
parser.add_argument("--model", type=Path, default=Path("data/model/random_forest_model.joblib"))
parser.add_argument("--output", type=Path, default=Path("data/model/random-forest-feature-importance.pptx"))
```

- [ ] **Step 5: Add atomic-failure regression tests**

Create a sentinel output, force save failure and corrupt-package validation failure separately, then assert sentinel bytes remain unchanged and no sibling temporary `.pptx` remains.

- [ ] **Step 6: Run focused and full Python tests**

```powershell
python -m unittest tests.test_create_random_forest_feature_importance_powerpoint -v
python -W error::ResourceWarning -m unittest discover -s tests -p 'test_*.py' -v
```

Expected: all tests pass.

- [ ] **Step 7: Generate and inspect the real deck**

```powershell
python scripts/create_random_forest_feature_importance_powerpoint.py
```

Reopen the result and independently compare its six labels, percentages, bar-width ratios, and three insights against a fresh `feature_importances_` read.

- [ ] **Step 8: Commit Task 2**

```powershell
git add scripts/create_random_forest_feature_importance_powerpoint.py tests/test_create_random_forest_feature_importance_powerpoint.py data/model/random-forest-feature-importance.pptx
git commit -m "feat: add random forest feature importance slide"
```

### Task 3: Documentation and complete verification

**Files:**
- Modify: `README.md`
- Modify: `progress.md`
- Modify: `todo.md`

**Interfaces:**
- Consumes: final verified generator and PowerPoint.
- Produces: reproducible instructions and project completion evidence.

- [ ] **Step 1: Document output and rerun command**

Add the artifact path and:

```powershell
python scripts/create_random_forest_feature_importance_powerpoint.py
```

Explain that importances show model reliance rather than causality and list all six current values.

- [ ] **Step 2: Record completion and measurements**

Add a completed feature-importance section to `todo.md`. Append to `progress.md` the ranked values, spatial and temporal totals, artifact size, SHA-256, and verification evidence.

- [ ] **Step 3: Run complete verification**

```powershell
python -W error::ResourceWarning -m unittest discover -s tests -p 'test_*.py' -v
npm.cmd test -- --run
npm.cmd run build
python scripts/create_random_forest_feature_importance_powerpoint.py
```

Expected: Python and Vitest pass; build succeeds with only the accepted large-chunk warning; deck regeneration succeeds.

- [ ] **Step 4: Independently inspect the artifact**

Verify ZIP integrity, one 16:9 slide, six ranked bars, percentage and insight agreement with the real model, East Asian font metadata, all shapes in bounds, byte size, and SHA-256.

- [ ] **Step 5: Check scope and commit**

```powershell
git diff --check
git status --short
git add README.md progress.md todo.md data/model/random-forest-feature-importance.pptx
git commit -m "docs: record feature importance chart"
```

Expected status before commit: only these intended changes plus the user’s pre-existing untracked `決策樹簡報小白解釋.txt`.

