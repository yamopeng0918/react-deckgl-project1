# Progress

## Project

Project name: 台灣地震熱區探索器

Workspace path: `C:\Users\yamopeng\OneDrive\桌面\taiwan-earthquake-visualization-prd`

## Current Status

The local MVP is implemented and documented. Remaining work is limited to optional heat-area click summaries and manual visual inspection of layer readability.

Completed so far:

- Clarified the MVP direction through product discovery.
- Confirmed the main user is the project owner.
- Confirmed the core screen is a Taiwan earthquake heatmap.
- Confirmed heatmap priority is earthquake frequency first.
- Confirmed earthquake points, year filtering, magnitude filtering, map pan/zoom, and click summaries as desired MVP features.
- Confirmed the project will use existing local CSV data.
- Confirmed data cleaning should produce a clean merged dataset and a rerunnable script.
- Confirmed local execution is the completion target; public deployment is out of scope for the MVP.
- Created the PRD at `docs/product-requirements/taiwan-earthquake-visualization-prd.md`.
- Renamed the project workspace content into `taiwan-earthquake-visualization-prd`.

## Key Product Decisions

- MVP audience: project owner.
- Primary view: Taiwan earthquake heatmap.
- Required data range: 1995-2024; 2025 included only if its format can be handled cleanly.
- Required interactions: map pan/zoom, year filter, magnitude filter, earthquake point display.
- Nice-to-have interaction: click a point or heat area to show summary information.
- Out of scope: earthquake prediction, 3D scene, global/Asia data, realtime updates, polished mobile adaptation, public deployment.
- Preferred technical direction: Python data processing, React frontend, deck.gl map visualization.

## Important Files

- PRD: `docs/product-requirements/taiwan-earthquake-visualization-prd.md`
- Source data folder: `(彭元懋)_台灣地震活動彙整`
- Project tracking: `progress.md`, `todo.md`

## Notes

- The original folder `pb_codex_tmp` could not be renamed directly because Windows reported it was in use.
- Project content was moved into `taiwan-earthquake-visualization-prd`.
- The old `pb_codex_tmp` folder was empty afterward but could not be removed due to access restrictions.

## 2026-07-01 Data Audit

- Inspected all CSV files under `(彭元懋)_台灣地震活動彙整`.
- Found 30 yearly CSV files for 1995-2024 and 9 monthly CSV files for 2025-01 through 2025-09.
- Confirmed all 39 CSV files use the same columns: `編號`, `地震時間`, `經度`, `緯度`, `規模`, `深度`, `最大震度`, `位置`.
- Confirmed required visualization fields are available: event time, longitude, latitude, magnitude, depth, and location text.
- Confirmed 2025 monthly files can be included automatically in the MVP data pipeline because their format matches the 1995-2024 yearly files.
- Total audited rows: 16,365.
- CSV files are readable with the Windows default/Big5-compatible encoding; UTF-8 decoding produces garbled Chinese text.

## 2026-07-01 Data Processing Pipeline

- Added `scripts/process_earthquakes.py` as the rerunnable CSV cleaning and merge script.
- Added `tests/test_process_earthquakes.py` covering yearly CSV input, 2025 monthly CSV input, normalized output fields, and invalid row exclusion.
- Generated frontend-ready JSON at `public/data/earthquakes.json`.
- Generated review-friendly CSV at `data/processed/earthquakes.csv`.
- Current generated dataset includes 39 source CSV files, 16,365 input rows, 16,365 exported rows, and 0 invalid rows.
- Included years are 1995-2025. The 2025 data currently covers January through September based on the available source files.
- Output fields are `id`, `event_time`, `year`, `longitude`, `latitude`, `magnitude`, `depth_km`, `max_intensity`, `location`, and `source_file`.
- Rerun command: `python scripts\process_earthquakes.py`.

## 2026-07-01 Frontend Direction

- Selected mockup direction: `docs/mockups/mockup-3-explorer-workbench.html`.
- The frontend should use the explorer workbench layout: top header, left filters, central map, right heat area summary, lower event table, and selected event details.
- Keep the original third-version data richness in the normal workbench. Use one-click map focus mode for a cleaner map view instead of individual collapsible panels.

## 2026-07-01 Frontend MVP Implementation

- Added a Vite React frontend at the project root.
- Added deck.gl and MapLibre rendering in `src/App.jsx`.
- The app loads `public/data/earthquakes.json`.
- Implemented a Taiwan map workbench based on the selected third mockup: top header, left filter panel, central map, right heat area summary, lower event table, and selected-event details.
- Removed individual collapsible data panels. The normal workbench now keeps filters, heat area summary, event table, and selected-event details expanded.
- Implemented year and magnitude filters. Filter changes update the heatmap layer, point layer, visible count, heat summaries, and event table.
- Implemented `HeatmapLayer` for frequency heat areas and `ScatterplotLayer` for earthquake points.
- Implemented map pan and zoom through deck.gl controller.
- Implemented point click behavior to update selected-event details.
- Added basic legend and visible filtered count.
- Added one-click map focus mode. The header button switches between `全螢幕地圖` and `回到工作台`; focus mode hides filters, heat summaries, the event table, and selected-event details so the map fills the workspace.
- Added frontend tests:
  - `src/lib/earthquakeData.test.js`
  - `src/App.test.jsx`
- Verification run:
  - `npm.cmd test -- --run` passed: 2 test files, 7 tests.
  - `npm.cmd run build` passed.
  - `http://127.0.0.1:5173/` returned HTTP 200 after starting the dev server.
- Local app URL: `http://127.0.0.1:5173/`.
- Known limitation: Vite build reports large chunk warnings because deck.gl and MapLibre are large dependencies. This is acceptable for the local MVP.
- Known limitation: base map tiles load from OpenStreetMap, so the background map requires network access. Earthquake data and deck.gl layers are local.

## 2026-07-01 Wrap-Up

- Added `README.md` with local setup, data processing, app startup, verification commands, included data years, MVP scope, and known limitations.
- Documentation tasks in `todo.md` are complete.
- Current local app URL: `http://127.0.0.1:5173/`.
- Final verification commands to run before handoff:
  - `python -m unittest tests.test_process_earthquakes -v`
  - `npm.cmd test -- --run`
  - `npm.cmd run build`
- Remaining todo items:
  - Optional: heat-area click summary.
  - Manual check: confirm heatmap and point layers remain readable together in the browser.

## 2026-07-06 Follow-Up Verification

- Confirmed the local Vite app is still reachable at `http://127.0.0.1:5173/` with HTTP 200.
- Re-ran backend data processing tests: `python -m unittest tests.test_process_earthquakes -v` passed, 2 tests.
- Re-ran frontend tests: `npm.cmd test -- --run` passed, 2 test files and 7 tests.
- Re-ran production build: `npm.cmd run build` passed. The existing large chunk warning remains expected because deck.gl and MapLibre are large dependencies.
- Checked layer configuration in `src/App.jsx`: heatmap and point layers are both present, point markers use translucent dark red fill plus white outline, and layer toggles can show both layers together.
- Attempted automated browser screenshot checks with local Edge and Chrome headless, but this environment returned no screenshot or DOM output. The remaining browser-readability item should still be verified manually in the live browser.
- `git` is not available in the current shell PATH, so worktree status could not be checked from this session.

## 2026-07-06 Additional Mockup Directions

- Added three visually distinct standalone HTML mockups under `docs/mockups/`:
  - `mockup-4-seismic-control-room.html`: dark operational control-room dashboard.
  - `mockup-5-cartographic-atlas.html`: bright cartographic atlas layout.
  - `mockup-6-data-lab-matrix.html`: table-first data lab layout.

## 2026-07-06 Mockup 6 Implementation

- Implemented the `mockup-6-data-lab-matrix.html` direction in the React app.
- Reworked `src/App.jsx` into a table-first data lab layout: header, top filter row, left event table, lower monthly activity chart, right synchronized map, and selected event summary.
- Kept MVP behavior: local JSON data load, year filter, magnitude filter, heatmap layer, point layer, map pan/zoom, point click selection, table row selection, and focused map mode.
- Updated `src/styles.css` to match the mockup 6 visual system with a restrained data-lab palette, dense panels, stable table/map/chart dimensions, and compact controls.
- Updated `src/App.test.jsx` with tests for the mockup 6 layout, top-row filtering, table-to-summary selection sync, and focused map mode.
- Verification:
  - First ran the new App tests and confirmed they failed against the old workbench layout.
  - `npm.cmd test -- --run src/App.test.jsx` passed: 4 tests.
  - `npm.cmd test -- --run` passed: 2 test files, 7 tests.
  - `npm.cmd run build` passed. The existing deck.gl / MapLibre large chunk warning remains expected.
  - `python -m unittest tests.test_process_earthquakes -v` passed: 2 tests.
  - `http://127.0.0.1:5173/` returned HTTP 200.

## 2026-07-06 Map and Load Responsiveness Fix

- Investigated the post-mockup-6 issue where the page could become unresponsive during data load and the map did not reliably display.
- Root cause found:
  - The mockup 6 table rendered every filtered earthquake row. With the real frontend dataset this means 16,365 table rows on initial load.
  - The data-lab grid used viewport minimum height but did not lock the app/workspace to a stable viewport height, which can leave deck.gl / MapLibre with an unstable parent size.
- Added a regression test in `src/App.test.jsx` using a 300-row dataset. The test first failed because all rows were rendered.
- Updated `src/App.jsx` so the event table renders only the latest 100 rows while the header still reports the full filtered count.
- Optimized table sorting to compare ISO event-time strings directly instead of constructing `Date` objects for every row.
- Updated `src/styles.css` so the app shell uses fixed viewport height, the workspace clips internal overflow, and the map panel uses an explicit grid row for the map canvas.
- Verification:
  - `npm.cmd test -- --run src/App.test.jsx` passed: 5 tests.
  - `npm.cmd test -- --run` passed: 2 test files, 8 tests.
  - `npm.cmd run build` passed. The existing deck.gl / MapLibre large chunk warning remains expected.
  - `python -m unittest tests.test_process_earthquakes -v` passed: 2 tests.
  - Confirmed `public/data/earthquakes.json` has 16,365 records.
  - `http://127.0.0.1:5173/` returned HTTP 200.

## 2026-07-06 Selected Panel Fix

- Investigated why the Selected panel appeared unresponsive after clicking table rows.
- Root cause found: the real dataset has many duplicate `id` values. For example, `小區域有感地震` appears 11,913 times, and yearly ids like `001` appear across many source files.
- The React app previously matched selected rows by `id` only, so clicking a row with a duplicate id could select the first matching record instead of the clicked record.
- Added a regression test in `src/App.test.jsx` with duplicate source ids. The test first failed because the selected details stayed on the wrong source file.
- Updated `src/App.jsx` to identify records by a stable composite key: `source_file + id + event_time`.
- The selected table row, map selection overlay, and selected event summary now use the same stable record identity.
- Verification:
  - `npm.cmd test -- --run src/App.test.jsx` passed: 6 tests.
  - `npm.cmd test -- --run` passed: 2 test files, 9 tests.
  - `npm.cmd run build` passed. The existing deck.gl / MapLibre large chunk warning remains expected.
  - `python -m unittest tests.test_process_earthquakes -v` passed: 2 tests.
  - `http://127.0.0.1:5173/` returned HTTP 200.

## 2026-07-06 Performance Optimization

- Investigated frontend responsiveness after the map/load and Selected panel fixes.
- Root cause found: the frontend dataset is already chronological ascending, but the app copied and sorted the full filtered record list again on every filter change before taking the latest 100 table rows.
- Updated `src/App.jsx` to prepare earthquake records once after loading:
  - precompute stable `record_key` values used by table selection, map selection, and the Selected panel.
  - precompute `event_month` values used by the monthly activity chart.
  - sort records once by latest event time first.
- Removed repeated full-list table sorting during render. The visible table now slices the first 100 records from the already-prepared filtered list.
- Updated monthly aggregation to use the precomputed `event_month` value instead of parsing the event time repeatedly.
- Verification:
  - `npm.cmd test -- --run src/App.test.jsx` passed: 6 tests.
  - `npm.cmd test -- --run` passed: 2 test files, 9 tests.
  - `npm.cmd run build` passed. The existing deck.gl / MapLibre large chunk warning remains expected.
  - `python -m unittest tests.test_process_earthquakes -v` passed: 2 tests.
  - `http://127.0.0.1:5173/` returned HTTP 200.

## 2026-07-06 Responsive Layout Update

- Added basic RWD support for the mockup 6 data-lab interface without changing the desktop layout.
- Removed the fixed desktop `body` minimum width so narrow screens are no longer forced into a 980px viewport.
- Added a tablet breakpoint at `1100px`:
  - filters collapse from five columns to two columns.
  - the workspace changes from two columns to one column.
  - the map and Selected panel are ordered before the table and monthly chart.
  - page overflow switches to vertical scrolling while map focus mode remains full-height.
- Added a mobile breakpoint at `640px`:
  - header content wraps cleanly.
  - filters collapse to one column.
  - map, table, details, and chart use tighter spacing and stable heights.
  - the event table remains horizontally scrollable instead of squeezing columns.
- Added `src/styles.test.js` as a CSS regression test for the RWD breakpoints and narrow viewport behavior.
- Verification:
  - First ran `npm.cmd test -- --run src/styles.test.js` and confirmed it failed against the old non-responsive CSS.
  - `npm.cmd test -- --run src/styles.test.js` passed: 2 tests.
  - `npm.cmd test -- --run src/App.test.jsx` passed: 6 tests.
  - `npm.cmd test -- --run` passed: 3 test files, 11 tests.
  - `npm.cmd run build` passed. The existing deck.gl / MapLibre large chunk warning remains expected.
  - `python -m unittest tests.test_process_earthquakes -v` passed: 2 tests.
  - `http://127.0.0.1:5173/` returned HTTP 200.

## 2026-07-06 Dark Theme Mode

- Added a header theme toggle for switching between light and dark modes.
- The theme preference is persisted in `localStorage` under `earthquake-theme`.
- The app defaults to light mode when no saved preference exists.
- Saved dark mode is restored on the next page load.
- Added a `theme-dark` root shell class and CSS variable overrides for:
  - app background and text.
  - panels, controls, buttons, borders, table headers, hover rows, and selected rows.
  - magnitude badges, chart colors, map canvas grid/background, and map selected overlay.
- Added `src/theme.test.jsx` covering theme toggle behavior and saved preference restoration.
- Verification:
  - First ran `npm.cmd test -- --run src/theme.test.jsx` and confirmed it failed against the app without dark theme support.
  - `npm.cmd test -- --run src/theme.test.jsx` passed: 2 tests.
  - `npm.cmd test -- --run` passed: 4 test files, 13 tests.
  - `npm.cmd run build` passed. The existing deck.gl / MapLibre large chunk warning remains expected.
  - `python -m unittest tests.test_process_earthquakes -v` passed: 2 tests.
  - `http://127.0.0.1:5173/` returned HTTP 200.

## 2026-07-06 Focused Map Point Layer Fix

- Investigated why earthquake point markers disappeared after pressing the focused map button.
- Root cause found: normal mode rendered `MapPanel` inside the stable `.map-panel` container, but focused mode rendered `.map-canvas` directly as the grid child. That changed the parent sizing/positioning environment used by deck.gl when the map was remounted.
- Updated focused map mode to wrap `MapPanel` in a dedicated `.map-panel.focus-map-panel` container.
- Added CSS so `.focus-map-panel` fills the header-free map area with a single full-height map row and no decorative border.
- Added `src/focusedMap.test.jsx` covering focused mode map container stability and preserving the visible `ScatterplotLayer` point data.
- Verification:
  - First ran `npm.cmd test -- --run src/focusedMap.test.jsx` and confirmed it failed against the previous focused map layout.
  - `npm.cmd test -- --run src/focusedMap.test.jsx` passed: 1 test.
  - `npm.cmd test -- --run` passed: 5 test files, 14 tests.
  - `npm.cmd run build` passed. The existing deck.gl / MapLibre large chunk warning remains expected.
  - `python -m unittest tests.test_process_earthquakes -v` passed: 2 tests.
  - `http://127.0.0.1:5173/` returned HTTP 200.

## 2026-07-06 Focused Map Point Visibility Follow-Up

- Investigated the remaining report that focused map mode still did not show earthquake event points.
- Root cause found: focused mode reused the normal `showPoints` layer visibility state. If the point layer had been disabled before entering focused mode, `ScatterplotLayer.visible` stayed `false` while the point toggle UI was hidden.
- Updated the point layer so focused map mode always shows earthquake points: `visible: mapFocus || showPoints`.
- Strengthened focused mode point visibility with:
  - brighter point fill color.
  - `radiusMinPixels` and `radiusMaxPixels` for stable on-screen marker size.
  - `parameters: { depthTest: false }` so points are drawn reliably above the heat layer.
- Extended `src/focusedMap.test.jsx` to verify that focused mode forces point visibility even after the normal point checkbox was turned off.
- Verification:
  - First ran `npm.cmd test -- --run src/focusedMap.test.jsx` and confirmed it failed with `ScatterplotLayer.visible=false`.
  - `npm.cmd test -- --run src/focusedMap.test.jsx` passed: 2 tests.
  - `npm.cmd test -- --run` passed: 5 test files, 15 tests.
  - `npm.cmd run build` passed. The existing deck.gl / MapLibre large chunk warning remains expected.
  - `python -m unittest tests.test_process_earthquakes -v` passed: 2 tests.
  - `http://127.0.0.1:5173/` returned HTTP 200.

## 2026-07-06 Year Range Control Merge

- Merged the separate `Year Min` and `Year Max` controls into one `Year Range` control.
- The new control displays the active year interval as `start - end`.
- Internally it keeps two range handles:
  - `Year range start` updates `yearMin`.
  - `Year range end` updates `yearMax`.
- Added guard logic so the year start cannot move past the current end, and the year end cannot move before the current start.
- Updated the filter row from five columns to four columns to match the merged control count.
- Added `src/yearRange.test.jsx` covering the merged year range UI and filtering behavior.
- Updated the existing App filter test to use `Year range start` instead of the removed `Year Min` control.
- Verification:
  - First ran `npm.cmd test -- --run src/yearRange.test.jsx` and confirmed it failed against the old two-control year UI.
  - `npm.cmd test -- --run src/yearRange.test.jsx` passed: 1 test.
  - `npm.cmd test -- --run src/App.test.jsx` passed: 6 tests.
  - `npm.cmd test -- --run` passed: 6 test files, 16 tests.
  - `npm.cmd run build` passed. The existing deck.gl / MapLibre large chunk warning remains expected.
  - `python -m unittest tests.test_process_earthquakes -v` passed: 2 tests.
  - `http://127.0.0.1:5173/` returned HTTP 200.

## 2026-07-06 Layout Overlap Prevention

- Investigated block overlap after recent filter and layout changes.
- Root cause found: the data-lab shell still used fixed grid rows `58px 76px 1fr`, but the merged `Year Range` control is taller than the old single-slider controls. The filter row could be forced into a 76px row and visually collide with the workspace below.
- Updated `src/styles.css` so the main shell uses content-aware rows: `auto auto minmax(0, 1fr)`.
- Added a `min-height` to the header instead of forcing a fixed row height.
- Allowed the filter row to stretch its controls to their actual content height.
- Changed normal page overflow to allow vertical scrolling when the viewport is too short for all panels.
- Relaxed workspace overflow so panels are not clipped into each other.
- Updated panel headers to use content padding and wrapping-friendly note text, preventing long notes from covering adjacent header text.
- Added a CSS regression test in `src/styles.test.js` to prevent fixed header/filter rows from returning.
- Verification:
  - First ran `npm.cmd test -- --run src/styles.test.js` and confirmed it failed against the fixed `58px 76px 1fr` layout.
  - `npm.cmd test -- --run src/styles.test.js` passed: 3 tests.
  - `npm.cmd test -- --run src/App.test.jsx` passed: 6 tests.
  - `npm.cmd test -- --run src/yearRange.test.jsx` passed: 1 test.
  - `npm.cmd test -- --run` passed: 6 test files, 17 tests.
  - `npm.cmd run build` passed. The existing deck.gl / MapLibre large chunk warning remains expected.
  - `python -m unittest tests.test_process_earthquakes -v` passed: 2 tests.
  - `http://127.0.0.1:5173/` returned HTTP 200.

## 2026-07-06 Event Table Panel Scroll Restore

- Restored the previous event-table scrolling behavior after the overlap-prevention change.
- Root cause found: changing the workspace overflow to visible allowed the event table panel to participate in page-level expansion instead of keeping its own internal scroll area.
- Kept the overlap fix for header and filter rows by retaining content-aware shell rows: `auto auto minmax(0, 1fr)`.
- Updated desktop layout so:
  - `.app-shell` has a fixed usable height of `max(720px, 100vh)`.
  - `.workspace` clips its internal grid with `overflow: hidden`.
  - `.table-panel` remains the scroll container with `overflow: auto`.
- Tablet and mobile breakpoints still use page-level vertical flow through their existing overrides.
- Added a CSS regression test to prevent the event table from losing its panel-local scroll behavior again.
- Verification:
  - First ran `npm.cmd test -- --run src/styles.test.js` and confirmed it failed while `.workspace` still used `overflow: visible`.
  - `npm.cmd test -- --run src/styles.test.js` passed: 4 tests.
  - `npm.cmd test -- --run src/App.test.jsx` passed: 6 tests.
  - `npm.cmd test -- --run src/yearRange.test.jsx` passed: 1 test.
  - `npm.cmd test -- --run` passed: 6 test files, 18 tests.
  - `npm.cmd run build` passed. The existing deck.gl / MapLibre large chunk warning remains expected.
  - `python -m unittest tests.test_process_earthquakes -v` passed: 2 tests.
  - `http://127.0.0.1:5173/` returned HTTP 200.

## 2026-07-07 Session Wrap-Up

- Completed the current UI and interaction cleanup pass for the mockup 6 data-lab interface.
- Current frontend state:
  - mockup 6 layout is implemented as the active React interface.
  - data loading is optimized by preparing records once after fetch.
  - the event table renders only the latest 100 visible rows and scrolls inside its own panel on desktop.
  - Selected event details use a stable composite record key, so duplicate source ids no longer break selection.
  - focused map mode keeps a stable map container and forces earthquake point visibility.
  - dark theme mode is available from the header and persists through `localStorage`.
  - RWD support is in place for desktop, tablet, and mobile breakpoints.
  - `Year Range` is now a single visual track with two draggable thumbs for start and end years.
- Current test coverage includes:
  - app layout and interaction tests in `src/App.test.jsx`.
  - responsive CSS regression tests in `src/styles.test.js`.
  - dark theme tests in `src/theme.test.jsx`.
  - focused map point visibility tests in `src/focusedMap.test.jsx`.
  - year range control tests in `src/yearRange.test.jsx`.
  - data processing tests in `tests/test_process_earthquakes.py`.
- Final verification on 2026-07-07:
  - `npm.cmd test -- --run` passed: 6 test files, 18 tests.
  - `npm.cmd run build` passed. The existing deck.gl / MapLibre large chunk warning remains expected.
  - `python -m unittest tests.test_process_earthquakes -v` passed: 2 tests.
  - `http://127.0.0.1:5173/` returned HTTP 200.
- Known remaining notes:
  - The build still reports large chunk warnings because deck.gl and MapLibre are large dependencies; this remains acceptable for the local MVP.
  - Base map tiles still depend on OpenStreetMap network access; earthquake data and deck.gl layers are local.
  - Optional heat-area click summary remains the only unimplemented optional frontend todo.

## 2026-07-06 Single Year Range Slider

- Updated the `Year Range` control from two range inputs to one range input.
- The single slider now controls only the start year.
- The range end is fixed to the dataset maximum year, so the displayed interval remains `start - latest year`.
- Simplified `updateYearRange` so it updates `yearMin` and resets `yearMax` to the current dataset max year.
- Renamed the year slider wrapper CSS from `.range-pair` to `.single-range`.
- Updated `src/yearRange.test.jsx` to verify that only one `Year range start` slider exists and `Year range end` is removed.
- Verification:
  - First ran `npm.cmd test -- --run src/yearRange.test.jsx` and confirmed it failed while the second `Year range end` slider still existed.
  - `npm.cmd test -- --run src/yearRange.test.jsx` passed: 1 test.
  - `npm.cmd test -- --run src/App.test.jsx` passed: 6 tests.
  - `npm.cmd test -- --run src/styles.test.js` passed: 4 tests.
  - `npm.cmd test -- --run` passed: 6 test files, 18 tests.
  - `npm.cmd run build` passed. The existing deck.gl / MapLibre large chunk warning remains expected.
  - `python -m unittest tests.test_process_earthquakes -v` passed: 2 tests.
  - `http://127.0.0.1:5173/` returned HTTP 200.

## 2026-07-06 Single-Track Dual-Thumb Year Range

- Updated `Year Range` to use one visual slider track with two draggable thumbs.
- The left thumb controls `yearMin`; the right thumb controls `yearMax`.
- Restored the full year interval behavior while keeping the UI visually as one slider.
- Prevented thumb crossover by clamping start to the current end and end to the current start.
- Implemented the single visual track with `.dual-range`, CSS custom properties `--range-start` and `--range-end`, and two overlaid range inputs.
- Updated `src/yearRange.test.jsx` to verify:
  - `.dual-range` is present.
  - the old `.range-pair` stacked layout is absent.
  - both `Year range start` and `Year range end` controls exist.
  - both endpoints can update filtering.
- Verification:
  - First ran `npm.cmd test -- --run src/yearRange.test.jsx` and confirmed it failed while the app still had the single-thumb implementation.
  - `npm.cmd test -- --run src/yearRange.test.jsx` passed: 1 test.
  - `npm.cmd test -- --run src/App.test.jsx` passed: 6 tests.
  - `npm.cmd test -- --run src/styles.test.js` passed: 4 tests.
  - `npm.cmd test -- --run` passed: 6 test files, 18 tests.
  - `npm.cmd run build` passed. The existing deck.gl / MapLibre large chunk warning remains expected.
  - `python -m unittest tests.test_process_earthquakes -v` passed: 2 tests.
  - `http://127.0.0.1:5173/` returned HTTP 200.

## 2026-07-07 Year Range Sensitivity Fix

- Investigated why `Year Range` felt insensitive after switching to the single visual track with two thumbs.
- Root cause found: the control used two overlaid native range inputs with pointer events only on the thumbs, so clicking or dragging the shared track did not reliably move an endpoint unless the user hit the thumb precisely.
- Updated `YearRangeControl` so the `.dual-range` track handles pointer down, move, up, and cancel events directly.
- The shared track now:
  - maps the pointer position to the nearest year.
  - selects the closest endpoint (`yearMin` or `yearMax`).
  - uses pointer capture when available so dragging remains stable.
  - keeps the native range inputs for keyboard and accessibility behavior.
- Added cursor and touch-action styling to make the shared slider track feel like an interactive drag surface.
- Added a regression test in `src/yearRange.test.jsx` proving that interacting with the shared track moves the nearest year thumb and updates filtering.
- Verification:
  - First ran `npm.cmd test -- --run src/yearRange.test.jsx` and confirmed the new track-interaction test failed before the fix.
  - `npm.cmd test -- --run src/yearRange.test.jsx` passed: 2 tests.
  - `npm.cmd test -- --run` passed: 6 test files, 19 tests.
  - `npm.cmd run build` passed. The existing deck.gl / MapLibre large chunk warning remains expected.
  - `python -m unittest tests.test_process_earthquakes -v` passed: 2 tests.
  - `http://127.0.0.1:5173/` returned HTTP 200.

## 2026-07-07 Magnitude Range Control Merge

- Updated the magnitude filter to match the `Year Range` interaction design.
- Replaced separate `Magnitude Min` and `Magnitude Max` controls with one `Magnitude Range` block.
- Refactored the previous year-specific range component into a shared dual-endpoint range control used by both:
  - `Year Range` with integer year steps.
  - `Magnitude Range` with 0.1 magnitude steps.
- The shared range control keeps:
  - one visual track with two endpoint thumbs.
  - keyboard-accessible native range inputs.
  - track click/drag behavior that moves the nearest endpoint.
  - endpoint crossover prevention through the existing filter update guards.
- Updated the desktop filter row from four columns to three columns: `Year Range`, `Magnitude Range`, and `Layer`.
- Added `src/magnitudeRange.test.jsx` covering:
  - removal of separate `Magnitude Min` / `Magnitude Max` inputs.
  - presence of the new `Magnitude Range` start/end endpoints.
  - magnitude filtering through the start endpoint.
  - shared-track interaction moving the nearest magnitude endpoint.
- Verification:
  - First ran `npm.cmd test -- --run src/magnitudeRange.test.jsx` and confirmed it failed while the old separate magnitude sliders were still present.
  - `npm.cmd test -- --run src/magnitudeRange.test.jsx` passed: 2 tests.
  - `npm.cmd test -- --run` passed: 7 test files, 21 tests.
  - `npm.cmd run build` passed. The existing deck.gl / MapLibre large chunk warning remains expected.
  - `python -m unittest tests.test_process_earthquakes -v` passed: 2 tests.
  - `http://127.0.0.1:5173/` returned HTTP 200.

## 2026-07-07 Selected Summary Clipping Fix

- Investigated why data inside the `選取事件摘要` panel could be visually clipped.
- Root cause found: the desktop right column uses a fixed second row for the detail panel, while `.detail-panel` clips overflow. The six summary fact blocks can exceed the available panel body height.
- Updated `.detail-body` so the summary content area:
  - has `min-height: 0` as a grid child.
  - scrolls internally with `overflow: auto`.
  - aligns content to the top instead of stretching rows.
- Kept the existing fixed desktop panel layout intact, so the table and map layout do not expand unexpectedly.
- Added a CSS regression test in `src/styles.test.js` to ensure the selected-event summary body remains scrollable inside the panel.
- Verification:
  - First ran `npm.cmd test -- --run src/styles.test.js` and confirmed the new selected-summary scroll test failed before the CSS fix.
  - `npm.cmd test -- --run src/styles.test.js` passed: 5 tests.
  - `npm.cmd test -- --run` passed: 7 test files, 22 tests.
  - `npm.cmd run build` passed. The existing deck.gl / MapLibre large chunk warning remains expected.
  - `python -m unittest tests.test_process_earthquakes -v` passed: 2 tests.
  - `http://127.0.0.1:5173/` returned HTTP 200.

## 2026-07-07 UI Interaction Wrap-Up

- Completed the current UI interaction cleanup pass for the mockup 6 data-lab interface.
- Finalized controls and layout behavior:
  - `Year Range` uses one visual track with two endpoint thumbs.
  - `Year Range` track clicks/drags move the nearest endpoint, improving slider sensitivity.
  - `Magnitude Min` and `Magnitude Max` are merged into one `Magnitude Range` control with the same dual-endpoint design.
  - The filter row now contains three desktop controls: `Year Range`, `Magnitude Range`, and `Layer`.
  - The selected-event summary body scrolls internally, so detail data is no longer clipped by the fixed desktop panel height.
- Current focused regression coverage includes:
  - `src/yearRange.test.jsx` for year range merge and track interaction.
  - `src/magnitudeRange.test.jsx` for magnitude range merge and track interaction.
  - `src/styles.test.js` for responsive layout, desktop table scrolling, and selected-summary internal scrolling.
  - Existing app, theme, focused-map, and data processing tests remain in place.
- Final verification on 2026-07-07:
  - `npm.cmd test -- --run` passed: 7 test files, 22 tests.
  - `npm.cmd run build` passed. The existing deck.gl / MapLibre large chunk warning remains expected.
  - `python -m unittest tests.test_process_earthquakes -v` passed: 2 tests.
  - `http://127.0.0.1:5173/` returned HTTP 200.
- Remaining todo items are unchanged:
  - Optional: add click summary for heat areas.
  - Manual browser check: verify heatmap and point layers remain visually readable together.

## 2026-07-07 Update Folder Data Import

- Added earthquake events from:
  - `(彭元懋)_台灣地震活動彙整/update`
- Audited the update folder and found 9 monthly CSV files:
  - `地震活動彙整_202510.csv`
  - `地震活動彙整_202511.csv`
  - `地震活動彙整_202512.csv`
  - `地震活動彙整_202601.csv`
  - `地震活動彙整_202602.csv`
  - `地震活動彙整_202603.csv`
  - `地震活動彙整_202604.csv`
  - `地震活動彙整_202605.csv`
  - `地震活動彙整_202606.csv`
- Confirmed the existing data pipeline already discovers nested CSV files under the source folder, so the update files are included by rerunning `python scripts\process_earthquakes.py`.
- Updated `scripts/process_earthquakes.py` so exported `source_file` paths always use `/` separators via `Path.as_posix()`. This keeps record identity stable across Windows and non-Windows environments.
- Added `test_includes_update_subfolder_with_stable_source_path` in `tests/test_process_earthquakes.py` to cover update-folder ingestion and stable source paths.
- Regenerated:
  - `public/data/earthquakes.json`
  - `data/processed/earthquakes.csv`
- Updated `README.md` with the new dataset range and counts.
- Current generated dataset:
  - Source CSV files: 48
  - Input rows: 16,691
  - Exported rows: 16,691
  - Invalid rows: 0
  - Included years: 1995-2026
  - Rows from `update/`: 326
  - Latest included event: `2026-06-30T05:15:02`
- Verification:
  - First ran `python -m unittest tests.test_process_earthquakes -v` and confirmed the new update-folder test failed because Windows emitted `update\...` paths.
  - `python -m unittest tests.test_process_earthquakes -v` passed: 3 tests.
  - `npm.cmd test -- --run` passed: 7 test files, 22 tests.
  - `npm.cmd run build` passed. The existing deck.gl / MapLibre large chunk warning remains expected.
  - `http://127.0.0.1:5173/` returned HTTP 200.

## 2026-07-07 Update Data Wrap-Up

- Completed the update-folder data import and documentation pass.
- Current data outputs are regenerated and ready for the frontend:
  - `public/data/earthquakes.json`
  - `data/processed/earthquakes.csv`
- Current dataset status:
  - 48 source CSV files.
  - 16,691 exported earthquake records.
  - 326 records from `update/`.
  - included years are 1995-2026.
  - latest included event is `2026-06-30T05:15:02`.
- Documentation and test coverage are updated:
  - `README.md` now lists the 1995-2026 range, 48 source files, 16,691 records, and 326 update rows.
  - `tests/test_process_earthquakes.py` now verifies update-folder ingestion and stable `/` source paths.
  - `scripts/process_earthquakes.py` now emits POSIX-style `source_file` paths for stable record identity.
- Final verification on 2026-07-07:
  - `python -m unittest tests.test_process_earthquakes -v` passed: 3 tests.
  - `npm.cmd test -- --run` passed: 7 test files, 22 tests.
  - `npm.cmd run build` passed. The existing deck.gl / MapLibre large chunk warning remains expected.
  - `http://127.0.0.1:5173/` returned HTTP 200.
- Remaining todo items are unchanged:
  - Optional: add click summary for heat areas.
  - Manual browser check: verify heatmap and point layers remain visually readable together.
