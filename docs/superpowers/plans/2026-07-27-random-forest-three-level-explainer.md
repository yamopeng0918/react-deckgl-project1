# Random-Forest Three-Level Explainer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate a one-slide 16:9 PowerPoint that shows the real first three levels of a deterministic representative tree from the trained random forest and explains forest voting in Traditional Chinese.

**Architecture:** A focused Python generator loads and validates the existing joblib model, selects a representative estimator deterministically, converts its first three levels into plain node records, and draws those records as native PowerPoint shapes. A unittest module verifies selection, extracted model values, slide content, geometry, package integrity, and atomic output behavior.

**Tech Stack:** Python 3, scikit-learn, joblib, python-pptx, unittest, OpenXML ZIP inspection.

## Global Constraints

- Use the real model at `data/model/random_forest_model.joblib`; do not invent split rules.
- Display at most seven nodes: depth 0, 1, and 2.
- Use Traditional Chinese audience-facing feature names.
- State that the diagram is one tree among 200 and that the model classifies maximum intensity rather than predicting earthquakes.
- Produce exactly one 16:9 PowerPoint slide.
- Default output is `data/model/random-forest-three-level-explainer.pptx`.
- Preserve an existing output if generation or validation fails.

---

### Task 1: Deterministic representative-tree extraction

**Files:**
- Create: `scripts/create_random_forest_three_level_explainer.py`
- Test: `tests/test_create_random_forest_three_level_explainer.py`

**Interfaces:**
- Consumes: a fitted `sklearn.ensemble.RandomForestClassifier` loaded by joblib.
- Produces: `select_representative_tree(model) -> tuple[int, DecisionTreeClassifier]`
- Produces: `extract_three_levels(estimator, feature_names, class_labels) -> list[dict]`

- [ ] **Step 1: Write failing model-selection and extraction tests**

Build a small deterministic `RandomForestClassifier` fixture and assert:

```python
index_a, tree_a = select_representative_tree(model)
index_b, tree_b = select_representative_tree(model)
self.assertEqual(index_a, index_b)
self.assertIs(tree_a, tree_b)

nodes = extract_three_levels(tree_a, FEATURE_NAMES, list(model.classes_))
self.assertLessEqual(len(nodes), 7)
self.assertEqual(nodes[0]["depth"], 0)
self.assertTrue(all(node["depth"] <= 2 for node in nodes))
```

For every non-leaf record, compare `feature_index`, `threshold`, `samples`, and dominant class against `tree_a.tree_`.

- [ ] **Step 2: Run the focused test and verify failure**

Run:

```powershell
python -m unittest tests.test_create_random_forest_three_level_explainer -v
```

Expected: import failure because the generator module does not exist.

- [ ] **Step 3: Implement model validation and deterministic selection**

Define:

```python
FEATURE_NAMES = ("magnitude", "depth_km", "longitude", "latitude", "month", "hour")
FEATURE_LABELS = {
    "magnitude": "震級",
    "depth_km": "深度",
    "longitude": "經度",
    "latitude": "緯度",
    "month": "月份",
    "hour": "時刻",
}
```

Validate that the loaded object exposes non-empty `estimators_`, six input features, and classes compatible with 0–7. Determine the most frequent root feature. Rank eligible trees by:

```python
(
    root_feature != most_common_root_feature,
    -count_nodes_through_depth_two(tree),
    count_location_splits_through_depth_two(tree),
    estimator_index,
)
```

Select the lowest tuple so the output is deterministic and favors a complete, readable tree.

- [ ] **Step 4: Implement extraction of depths 0–2**

Traverse left child before right child and emit plain dictionaries containing:

```python
{
    "node_id": int,
    "parent_id": int | None,
    "branch": "yes" | "no" | None,
    "depth": int,
    "feature_index": int | None,
    "feature_name": str | None,
    "threshold": float | None,
    "samples": int,
    "dominant_class": int,
    "class_counts": tuple[float, ...],
    "is_leaf": bool,
}
```

Treat depth-two nodes as displayed endpoints even if the real tree continues, while preserving `is_leaf` as the real model value.

- [ ] **Step 5: Run focused extraction tests**

Run:

```powershell
python -m unittest tests.test_create_random_forest_three_level_explainer -v
```

Expected: selection and extraction tests pass.

- [ ] **Step 6: Commit the extraction layer**

```powershell
git add scripts/create_random_forest_three_level_explainer.py tests/test_create_random_forest_three_level_explainer.py
git commit -m "feat: extract representative random forest tree"
```

### Task 2: Native PowerPoint diagram generation

**Files:**
- Modify: `scripts/create_random_forest_three_level_explainer.py`
- Modify: `tests/test_create_random_forest_three_level_explainer.py`
- Create: `data/model/random-forest-three-level-explainer.pptx`

**Interfaces:**
- Consumes: node records from `extract_three_levels`.
- Produces: `build_deck(nodes, tree_index, estimator_count) -> Presentation`
- Produces: `create_random_forest_three_level_explainer(model_path, output_path) -> Path`

- [ ] **Step 1: Write failing slide-content and package tests**

Create a temporary model, generate a deck, reopen it, and assert:

```python
self.assertEqual(len(deck.slides), 1)
self.assertAlmostEqual(deck.slide_width / deck.slide_height, 16 / 9, places=2)
for expected in (
    "隨機森林如何判斷最大震度？",
    "是（≤）",
    "否（>）",
    "200 棵樹中的一棵",
    "投票",
    "不是地震預測",
):
    self.assertIn(expected, slide_text)
```

Also assert all shapes remain within slide bounds and compare each displayed node threshold/sample/class string with freshly extracted node records.

- [ ] **Step 2: Run the focused test and verify failure**

Run:

```powershell
python -m unittest tests.test_create_random_forest_three_level_explainer -v
```

Expected: failure because deck construction functions are not implemented.

- [ ] **Step 3: Implement the 16:9 native-shape layout**

Use `Presentation()` with `13.333333 × 7.5` inches. Draw:

- title and subtitle at the top;
- root at x=5.19, y=1.18;
- depth-one nodes at x=2.15 and 8.23, y=2.65;
- depth-two nodes at x=0.45, 3.45, 6.45, and 9.45, y=4.20;
- connectors behind nodes with teal `是（≤）` and amber `否（>）` labels;
- a navy footer panel with the 200-tree voting explanation;
- a muted limitation line at the bottom.

Node copy format:

```python
f"{feature_label} ≤ {formatted_threshold}？\n樣本 {samples:,}｜目前偏向震度 {dominant_class}"
```

For a real leaf:

```python
f"此分支預測震度 {dominant_class}\n樣本 {samples:,}"
```

Use `Microsoft JhengHei`, a light paper background, high-contrast navy text, and color-blind-friendly teal/amber branches.

- [ ] **Step 4: Implement atomic save and CLI**

Load with `joblib.load`, build the slide, save to a temporary sibling file, verify ZIP integrity and one-slide 16:9 structure, then use `os.replace`. Provide defaults:

```python
parser.add_argument("--model", type=Path, default=Path("data/model/random_forest_model.joblib"))
parser.add_argument("--output", type=Path, default=Path("data/model/random-forest-three-level-explainer.pptx"))
```

- [ ] **Step 5: Run focused tests**

Run:

```powershell
python -m unittest tests.test_create_random_forest_three_level_explainer -v
```

Expected: all focused tests pass.

- [ ] **Step 6: Generate the real PowerPoint**

Run:

```powershell
python scripts/create_random_forest_three_level_explainer.py
```

Expected: prints `data\model\random-forest-three-level-explainer.pptx`.

- [ ] **Step 7: Commit the generator, tests, and deck**

```powershell
git add scripts/create_random_forest_three_level_explainer.py tests/test_create_random_forest_three_level_explainer.py data/model/random-forest-three-level-explainer.pptx
git commit -m "feat: add random forest logic explainer slide"
```

### Task 3: Documentation and full verification

**Files:**
- Modify: `README.md`
- Modify: `progress.md`
- Modify: `todo.md`

**Interfaces:**
- Consumes: the verified generator and generated deck.
- Produces: reproducible project documentation and final verification evidence.

- [ ] **Step 1: Document the artifact and rerun command**

Add the output path and:

```powershell
python scripts/create_random_forest_three_level_explainer.py
```

Explain that the slide shows a deterministic representative tree’s real first three levels and that final classification uses all 200 trees.

- [ ] **Step 2: Record completion**

Add a completed todo section for the explainer slide. Append the selected estimator index, root feature, generated file size, checksum, and verification commands to `progress.md`.

- [ ] **Step 3: Run complete verification**

Run:

```powershell
python -W error::ResourceWarning -m unittest discover -s tests -p 'test_*.py' -v
npm.cmd test -- --run
npm.cmd run build
python scripts/create_random_forest_three_level_explainer.py
```

Expected: all Python and Vitest tests pass; Vite build succeeds with only the accepted large-chunk warning; regenerating the deck succeeds.

- [ ] **Step 4: Independently inspect the final artifact**

Reopen the deck with `python-pptx` and ZIP inspection. Verify one slide, 16:9 dimensions, no corrupt ZIP member, required text, shapes within bounds, and actual displayed rules matching the selected estimator. Calculate SHA-256 and byte size.

- [ ] **Step 5: Check Git scope**

Run:

```powershell
git diff --check
git status --short
```

Expected: only intended files plus the user’s pre-existing untracked `決策樹簡報小白解釋.txt`.

- [ ] **Step 6: Commit documentation**

```powershell
git add README.md progress.md todo.md
git commit -m "docs: record random forest explainer slide"
```

