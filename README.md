# Taiwan Earthquake Hotspot Explorer

Interactive Taiwan earthquake explorer built with CSV data, React, and deck.gl.

Public URL:

```text
https://react-deckgl-project1-kappa.vercel.app/
```

## Current MVP

- Taiwan earthquake heatmap.
- Earthquake point layer.
- Year range filter.
- Magnitude range filter.
- Map pan and zoom.
- Event table with selected-event summary.
- Heat-area click summary.
- Yearly event count chart.
- Focused map mode.
- Dark theme mode.
- Rerunnable data processing pipeline.

## Data

Source data folder:

```text
(彭元懋)_台灣地震活動彙整
```

Included source files:

- 1995-2024 yearly CSV files.
- 2025 monthly CSV files from the original 2025 folder.
- 2025-10 through 2026-06 monthly CSV files from `update/`.

Generated outputs:

- Frontend JSON: `public/data/earthquakes.json`
- Review CSV: `data/processed/earthquakes.csv`

Current generated dataset:

- Source CSV files: 48
- Input rows: 16,691
- Exported rows: 16,691
- Invalid rows: 0
- Included years: 1995-2026
- Update rows added from `update/`: 326

## Setup

Requirements:

- Python
- Node.js
- npm

Install frontend dependencies:

```powershell
npm.cmd install
```

Use `npm.cmd` on PowerShell if `npm` does not resolve correctly.

## Run Data Processing

Regenerate frontend and processed data files:

```powershell
python scripts\process_earthquakes.py
```

## Run App

Start the local Vite app:

```powershell
npm.cmd run dev -- --host 127.0.0.1
```

Local URL:

```text
http://127.0.0.1:5173/
```

## Verification

Data processing tests:

```powershell
python -m unittest tests.test_process_earthquakes -v
```

Frontend tests:

```powershell
npm.cmd test -- --run
```

Production build:

```powershell
npm.cmd run build
```

## HyperFrames Video Environment

HeyGen HyperFrames is installed for HTML-to-video work.

Installed project tooling:

- `hyperframes@0.7.45`
- Local FFmpeg / FFprobe under `tools/ffmpeg/bin/`
- HyperFrames-managed Chrome Headless Shell cache

Check the video environment:

```powershell
npm.cmd run hf:doctor
```

Preview a HyperFrames composition:

```powershell
npm.cmd run hf:preview
```

Render a HyperFrames composition to video:

```powershell
npm.cmd run hf:render
```

Docker and local AI audio helpers are optional and are not required for basic local MP4 rendering.

Closing-report preview composition:

```powershell
npx.cmd hyperframes preview hyperframes/closing-report
npx.cmd hyperframes lint hyperframes/closing-report
npx.cmd hyperframes snapshot hyperframes/closing-report --frames 6 --describe false
```

Rendered closing-report video:

```text
hyperframes/closing-report/closing-report-model-results-final.mp4
```

Latest closing-report PowerPoint deliverables:

```text
hyperframes/closing-report/closing-report-model-results-final.pptx
hyperframes/closing-report/decision-tree-results.pptx
```

The closing-report PowerPoint has 14 scene slides. Slide 4 links to the one-page decision-tree result deck when both PPTX files remain in the same directory.

To regenerate it from the documented midpoint snapshots (in fixed scene order), run:

```powershell
python scripts/create_closing_report_powerpoint.py --output hyperframes/closing-report/closing-report-model-results-final.pptx
```

The generator validates that `hyperframes/closing-report/decision-tree-results.pptx` exists and is a readable PowerPoint package before creating the report.

## Vercel Deployment

This project is deployed as a Vite static frontend.

Current public deployment:

```text
https://react-deckgl-project1-kappa.vercel.app/
```

Vercel settings are recorded in `vercel.json`:

- Install command: `npm ci`
- Build command: `npm run build`
- Output directory: `dist`
- Node.js: `>=20.19.0`
- SPA fallback: all routes rewrite to `index.html`

Deployment source hygiene:

- Do not commit `node_modules/`.
- Do not commit generated `dist/`.
- Do not commit local logs or Python `__pycache__` files.
- `public/data/earthquakes.json` is the frontend data file that must be committed when the processed dataset changes.

## Maximum-Intensity Model Comparison

Install the Python model dependencies:

```powershell
python -m pip install -r requirements-model.txt
```

Train and evaluate each classifier independently with the current processed dataset, then rebuild the common comparison report:

```powershell
python scripts/train_intensity_classifier.py
python scripts/train_random_forest_intensity_classifier.py
python scripts/compare_intensity_models.py
```

Both pipelines normalize `5弱` / `5強` to class `5` and `6弱` / `6強` to class `6`. They use the same six features—magnitude, depth, longitude, latitude, event month, and event hour—and the same chronological design: 13,617 training records from 1995–2023 and 3,039 test records from 2024–2026. Of 16,691 input records, 35 with invalid or missing targets are excluded. Model selection uses only 2021–2023 validation data within the training period, so the 2024–2026 test period remains held out.

Generated reports are written to `data/model/`:

- Decision tree: `decision_tree_metrics.json`, `decision_tree_class_report.csv`, `decision_tree_confusion_matrix.csv`, and `decision_tree_confusion_matrix.png`.
- Random forest: `random_forest_metrics.json`, `random_forest_class_report.csv`, `random_forest_confusion_matrix.csv`, and `random_forest_confusion_matrix.png`.
- Shared comparison: `model_comparison.csv`.

The fitted `decision_tree_model.joblib` and `random_forest_model.joblib` files are generated locally and ignored by Git. Confusion-matrix rows are actual classes and columns are predicted classes.

Measured chronological test results:

- Decision tree: accuracy 0.2833168806; macro recall 0.3043045023.
- Random forest: accuracy 0.4389601843; macro recall 0.4080583025.

The selected random forest uses `n_estimators=200`, `max_depth=12`, `min_samples_leaf=1`, `max_features=sqrt`, `class_weight=balanced_subsample`, and `random_state=42`. Its 2021–2023 validation macro recall is 0.4206442216 and validation accuracy is 0.4582869855. On the chronological test set, recall/support by intensity is: 0 = 0.0000/1, 1 = 0.1938/289, 2 = 0.4319/1,278, 3 = 0.3978/910, 4 = 0.6487/538, 5 = 0.6842/19, 6 = 0.5000/4, and 7 = unavailable/0.

The random forest leads the decision tree on both chronological test macro recall and accuracy. This is a maximum-intensity classification comparison, not earthquake forecasting; estimates for rare classes remain unstable because the test set contains only one intensity-0 event, four intensity-6 events, and no intensity-7 events.

### Random-Forest Results PowerPoint

Regenerate the two-slide random-forest results deck with the default inputs and output path:

```powershell
python scripts/create_random_forest_results_powerpoint.py
```

The generated PowerPoint is written to:

```text
data/model/random-forest-results.pptx
```

Slide 1 summarizes the chronological test metrics, per-class recall/support, selected parameters, and rare-class warning. Slide 2 renders and embeds the confusion matrix directly from the validated metrics JSON (the legacy `--matrix` option is ignored) and explains the principal 2–4 震度類別 confusion and support limitation.

## Known Limitations

- Base map tiles use OpenStreetMap and require network access for the background map.
- Earthquake data and deck.gl layers are local after data processing.
- Vite build reports large chunk warnings because deck.gl and MapLibre are large dependencies; this is acceptable for the local MVP.
- Heatmap and point-layer readability should still be checked manually in the browser.
- The model results describe classification from recorded event attributes, not earthquake forecasting. Chronological test performance remains limited, and rare intensity classes have too few or no recent examples for stable recall estimates.
