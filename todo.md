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
- [x] Verify 1995-2024 data is included.
- [x] Verify 2025 handling is either included or clearly marked as excluded.
- [x] Verify year filtering changes map results.
- [x] Verify magnitude filtering changes map results.
- [ ] Verify heatmap and point layers remain readable together.
- [x] Verify the data processing script can be rerun from a clean state.

## Documentation

- [x] Update README with local setup instructions.
- [x] Document data source and included years.
- [x] Document MVP scope and out-of-scope items.
- [x] Document how to rerun data processing.
- [x] Record any known limitations.
