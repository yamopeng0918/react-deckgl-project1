# Frontend Workbench Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the approved collapsible explorer workbench as a local React/deck.gl MVP that reads the processed earthquake dataset.

**Architecture:** Create a Vite React app at the project root. Keep data behavior in small pure modules under `src/lib`, and keep the UI in focused React components under `src/components`. The app fetches `public/data/earthquakes.json`, filters records by year and magnitude, renders deck.gl heatmap and point layers, and exposes collapsible data panels based on mockup 3.

**Tech Stack:** React, Vite, Vitest, Testing Library, deck.gl, react-map-gl, MapLibre GL, Python data pipeline output.

## Global Constraints

- Use `docs/mockups/mockup-3-explorer-workbench.html` as the visual direction.
- Preserve the third-version data richness, but make data-heavy areas collapsible.
- Required MVP interactions: map pan/zoom, heatmap layer, point layer, year filter, magnitude filter, filtered count, and point click summary.
- Load data from `public/data/earthquakes.json`.
- Do not add earthquake prediction, 3D scenes, realtime updates, public deployment, or portfolio-style polish.
- Use `npm.cmd` on this Windows PowerShell environment.

---

### Task 1: Frontend Scaffold And Data Behavior

**Files:**
- Create: `package.json`
- Create: `index.html`
- Create: `src/main.jsx`
- Create: `src/lib/earthquakeData.js`
- Create: `src/lib/earthquakeData.test.js`
- Create: `src/setupTests.js`
- Create: `vite.config.js`

**Interfaces:**
- Produces: `getDatasetStats(records) -> { minYear, maxYear, minMagnitude, maxMagnitude, total }`
- Produces: `filterEarthquakes(records, filters) -> EarthquakeRecord[]`
- Produces: `formatEarthquakeTime(value) -> string`

- [ ] Write failing Vitest tests for dataset stats, year filtering, magnitude filtering, and time formatting.
- [ ] Run `npm.cmd test -- --run src/lib/earthquakeData.test.js` and confirm failure due to missing implementation.
- [ ] Implement `src/lib/earthquakeData.js`.
- [ ] Run `npm.cmd test -- --run src/lib/earthquakeData.test.js` and confirm tests pass.

### Task 2: Collapsible Workbench UI

**Files:**
- Create: `src/App.jsx`
- Create: `src/App.test.jsx`
- Create: `src/styles.css`
- Modify: `src/main.jsx`

**Interfaces:**
- Consumes: `filterEarthquakes`, `getDatasetStats`, and `formatEarthquakeTime`.
- Produces: rendered workbench UI with controls, collapsible panels, event table, and selected event details.

- [ ] Write failing component tests for loading dataset, filter count changing by year/magnitude controls, and collapsible table/details sections.
- [ ] Run `npm.cmd test -- --run src/App.test.jsx` and confirm expected failure.
- [ ] Implement the React workbench UI.
- [ ] Run `npm.cmd test -- --run src/App.test.jsx` and confirm tests pass.

### Task 3: deck.gl Map Layers And Local Verification

**Files:**
- Modify: `src/App.jsx`
- Modify: `src/styles.css`
- Modify: `todo.md`
- Modify: `progress.md`

**Interfaces:**
- Produces: heatmap and scatterplot layers controlled by filtered records and layer toggles.
- Produces: local dev server URL.

- [ ] Add deck.gl `HeatmapLayer` and `ScatterplotLayer` over a MapLibre base map.
- [ ] Wire point click to selected-event details.
- [ ] Run `npm.cmd test -- --run`.
- [ ] Run `npm.cmd run build`.
- [ ] Start `npm.cmd run dev -- --host 127.0.0.1`.
- [ ] Update tracking files with implemented features, verification output, and local URL.
