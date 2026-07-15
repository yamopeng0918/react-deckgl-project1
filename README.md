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

## Maximum-Intensity Decision Tree

Install the Python model dependencies:

```powershell
python -m pip install -r requirements-model.txt
```

Train and evaluate the classifier with the current processed dataset:

```powershell
python scripts/train_intensity_classifier.py
```

The model normalizes `5弱` / `5強` to class `5` and `6弱` / `6強` to class `6`. It trains on 1995–2023 records and evaluates only on 2024–2026 records. Features are magnitude, depth, longitude, latitude, event month, and event hour.

Generated reports are written to `data/model/`:

- `decision_tree_metrics.json`
- `decision_tree_class_report.csv`
- `decision_tree_confusion_matrix.csv`
- `decision_tree_confusion_matrix.png`

The fitted `decision_tree_model.joblib` is generated locally and ignored by Git. The confusion-matrix rows are actual classes and columns are predicted classes.

## Known Limitations

- Base map tiles use OpenStreetMap and require network access for the background map.
- Earthquake data and deck.gl layers are local after data processing.
- Vite build reports large chunk warnings because deck.gl and MapLibre are large dependencies; this is acceptable for the local MVP.
- Heatmap and point-layer readability should still be checked manually in the browser.
- The decision-tree result is a baseline classification model, not an earthquake prediction system. Chronological test performance is limited, and rare intensity classes have too few or no recent examples for stable recall estimates.
