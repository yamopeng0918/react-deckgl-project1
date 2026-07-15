# Decision Tree Results Slide Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate and verify a one-page PowerPoint summary of the current decision-tree model results.

**Architecture:** A small Python generator reads the existing metrics JSON and confusion-matrix PNG, builds one editable 16:9 slide, and saves it under `data/model/`. Verification inspects both the PowerPoint OpenXML package and slide text/media structure.

**Tech Stack:** Python, python-pptx, PowerPoint OpenXML

## Global Constraints

- Use only measured values from `decision_tree_metrics.json`.
- Keep the result to exactly one 16:9 slide.
- State rare-class limitations explicitly.
- Do not alter model outputs or source earthquake data.

---

### Task 1: Generate and verify the review slide

**Files:**
- Create: `scripts/create_decision_tree_results_slide.py`
- Create: `data/model/decision-tree-results-review.pptx`

**Interfaces:**
- Consumes: metrics JSON and confusion-matrix PNG.
- Produces: one-page PowerPoint review deck.

- [ ] Install `python-pptx` if unavailable.
- [ ] Implement a deterministic one-slide generator using the approved layout.
- [ ] Run the generator against current model artifacts.
- [ ] Verify OpenXML integrity, one-slide count, embedded media, and required slide text.
- [ ] Render or extract a visual preview and inspect the final slide.
