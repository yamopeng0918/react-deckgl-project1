# Todo

## Next Milestone: Data Audit

- [x] Inspect CSV columns for 1995-2024 files.
- [x] Inspect the 2025 folder structure and file format.
- [x] Identify required fields for visualization: event time, latitude, longitude, magnitude, depth, location/description.
- [x] Document any column naming differences across years.
- [x] Decide whether 2025 can be included automatically.

## Data Processing

- [x] Create a Python data cleaning script.
- [x] Read all supported yearly CSV files.
- [x] Normalize column names and data types.
- [x] Parse event time into a consistent format.
- [x] Validate latitude and longitude values.
- [x] Validate magnitude and depth values.
- [x] Merge cleaned records into one dataset.
- [x] Export a frontend-ready data file.
- [x] Add a simple rerun command or instruction.

## Frontend MVP

- [x] Scaffold the React frontend.
- [x] Add deck.gl map rendering.
- [x] Load the cleaned earthquake dataset.
- [x] Render Taiwan earthquake heatmap.
- [x] Render earthquake point layer.
- [x] Add year filter.
- [x] Add magnitude filter.
- [x] Make heatmap and points update with filters.
- [x] Support map pan and zoom.
- [x] Add basic legend and visible filter state.
- [x] Add click summary for earthquake points if time allows.
- [x] Add click summary for heat areas if time allows.

## Verification

- [x] Verify the local app starts successfully.
- [x] Verify the public Vercel deployment is reachable.
- [x] Verify 1995-2024 data is included.
- [x] Verify 2025 handling is either included or clearly marked as excluded.
- [x] Verify year filtering changes map results.
- [x] Verify magnitude filtering changes map results.
- [x] Verify heatmap and point layers remain readable together.
- [x] Verify the data processing script can be rerun from a clean state.

## Documentation

- [x] Update README with local setup instructions.
- [x] Document data source and included years.
- [x] Document MVP scope and out-of-scope items.
- [x] Document how to rerun data processing.
- [x] Record any known limitations.

## Maximum-Intensity Classification

- [x] Normalize historical and modern maximum-intensity labels to classes 0–7.
- [x] Train a decision-tree classifier on 1995–2023 data.
- [x] Evaluate chronologically on 2024–2026 data.
- [x] Report overall accuracy and per-class recall with support counts.
- [x] Export a labeled confusion matrix as CSV and PNG.
- [x] Add automated model and artifact tests.
- [x] Document the rerun command and rare-class limitations.

## Random-Forest Model Comparison

- [x] Add a rerunnable random-forest maximum-intensity classification pipeline using the common six-feature data preparation.
- [x] Select hyperparameters with chronological 2021–2023 validation data kept inside the 1995–2023 training period.
- [x] Generate random-forest metrics, class report, labeled confusion-matrix CSV/PNG, and a local ignored fitted model.
- [x] Compare the decision tree and random forest on the identical 2024–2026 chronological test basis.
- [x] Record measured validation/test results, per-class recall/support, and the honest rare-class limitation in project documentation.
- [x] Rerun both model pipelines, comparison, result-slide generation, Python/Vitest suites, production build, and PowerPoint package checks.

## Final Closing Report Deliverables

- [x] Update closing report page 4 with measured model results.
- [x] Update closing report page 5 with the completed model milestone.
- [x] Add the page-4 link to the one-page decision-tree result deck.
- [x] Re-render the 96-second closing report MP4.
- [x] Rebuild the closing report as a 14-slide PowerPoint.
- [x] Verify the final video and PowerPoint artifacts.

## Random-Forest Results PowerPoint

- [x] Add the rerunnable random-forest results PowerPoint generator.
- [x] Generate the real two-slide `data/model/random-forest-results.pptx` output.
- [x] Render and embed the slide-2 confusion matrix directly from the validated metrics JSON.
- [x] Independently validate ZIP integrity, two-slide structure, 16:9 dimensions, required text, slide-2 image relationship, generated media geometry, and independence from the legacy external PNG.
- [x] Document the exact rerun command, output path, measured results, artifact hash, and verification evidence.

## Random-Forest Three-Level Explainer

- [x] Add a rerunnable one-slide PowerPoint generator for a deterministic representative tree.
- [x] Generate `data/model/random-forest-three-level-explainer.pptx` from the fitted local random-forest model.
- [x] Show the selected estimator's real root through depth-two rules and explain that final classification uses all 200 forest votes.
- [x] Independently validate the PowerPoint package, one-slide 16:9 geometry, displayed rules, generated file size, and SHA-256 checksum.
- [x] Document the rerun command and final verification evidence.
