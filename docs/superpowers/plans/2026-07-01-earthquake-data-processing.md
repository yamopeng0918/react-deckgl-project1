# Earthquake Data Processing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a rerunnable Python data pipeline that merges the audited Taiwan earthquake CSV files into frontend-ready JSON and review-friendly CSV.

**Architecture:** Use a small standard-library Python module with pure functions for discovery, row normalization, validation, and export. Tests use temporary CSV fixtures so the pipeline behavior is proven without depending on the large source dataset.

**Tech Stack:** Python standard library, `unittest`, CSV input encoded with Windows default/Big5-compatible text, JSON and CSV outputs.

## Global Constraints

- Do not delete or overwrite source CSV files.
- Include 1995-2024 yearly CSV files.
- Include 2025 monthly CSV files because the data audit confirmed matching columns.
- Normalize fields to `id`, `event_time`, `year`, `longitude`, `latitude`, `magnitude`, `depth_km`, `max_intensity`, `location`, `source_file`.
- Export frontend data to `public/data/earthquakes.json`.
- Export review data to `data/processed/earthquakes.csv`.
- Update `progress.md` and `todo.md` after verification.

---

### Task 1: Tested Data Processor

**Files:**
- Create: `scripts/process_earthquakes.py`
- Create: `tests/test_process_earthquakes.py`

**Interfaces:**
- Produces: `process_dataset(source_dir: Path, json_output: Path, csv_output: Path) -> dict`
- Produces: command `python scripts/process_earthquakes.py`

- [ ] Write failing tests for 2025 inclusion, field normalization, invalid row exclusion, and exported summary.
- [ ] Run `python -m unittest tests.test_process_earthquakes -v` and confirm failure caused by missing implementation.
- [ ] Implement the processor using only Python standard-library modules.
- [ ] Run `python -m unittest tests.test_process_earthquakes -v` and confirm tests pass.

### Task 2: Generate MVP Data Outputs

**Files:**
- Create: `public/data/earthquakes.json`
- Create: `data/processed/earthquakes.csv`

**Interfaces:**
- Consumes: `scripts/process_earthquakes.py`
- Produces: frontend-readable earthquake records and printed validation summary.

- [ ] Run `python scripts/process_earthquakes.py`.
- [ ] Confirm output includes 1995-2025 and 16,365 cleaned records unless validation reports excluded rows.
- [ ] Inspect output files exist and contain normalized columns.

### Task 3: Tracking Updates

**Files:**
- Modify: `progress.md`
- Modify: `todo.md`

- [ ] Record generated output paths, row count, included years, and rerun command in `progress.md`.
- [ ] Mark completed data processing tasks in `todo.md`.
- [ ] Run final verification commands before reporting completion.
