# Decision Tree Results Slide Design

## Goal

Create one 16:9 PowerPoint slide that summarizes the chronological decision-tree evaluation clearly and honestly for review.

## Layout

- Header: title and short method subtitle.
- Left column: overall accuracy, train/test periods, record counts, and selected tree parameters.
- Lower-left: per-intensity recall bars with support counts for classes 0–7.
- Right column: the generated confusion matrix as the primary evidence visual.
- Footer: concise interpretation stating that this is a baseline model and rare-class recall is unstable.

## Visual Style

- Clean dark navy and warm off-white presentation palette.
- Accuracy is visually prominent without celebratory styling.
- Recall uses percentages and support counts together.
- Intensity 7 displays `N/A` because the test set has no examples.
- No claim of predictive readiness.

## Source

- Metrics: `data/model/decision_tree_metrics.json`.
- Matrix image: `data/model/decision_tree_confusion_matrix.png`.

## Output

- `data/model/decision-tree-results-review.pptx`.
- A PNG preview beside the PPTX when rendering support is available.

## Verification

- Exactly one widescreen slide.
- Required title, accuracy, periods, recall values, and limitation note are present.
- Confusion matrix is embedded.
- OpenXML ZIP integrity has no bad entries.
