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
hyperframes/closing-report/closing-report-full.mp4
hyperframes/closing-report/closing-report-full-transitions.mp4
```

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

## Known Limitations

- Base map tiles use OpenStreetMap and require network access for the background map.
- Earthquake data and deck.gl layers are local after data processing.
- Vite build reports large chunk warnings because deck.gl and MapLibre are large dependencies; this is acceptable for the local MVP.
- Heatmap and point-layer readability should still be checked manually in the browser.
