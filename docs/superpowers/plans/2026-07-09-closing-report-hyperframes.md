# Closing Report HyperFrames Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a previewable HyperFrames closing-report composition for the Taiwan Earthquake Hotspot Explorer.

**Architecture:** Keep the HyperFrames composition isolated from the existing Vite app by placing it in `hyperframes/closing-report/index.html`. Use static HTML/CSS with HyperFrames timing attributes so the first preview is easy to inspect and revise.

**Tech Stack:** HyperFrames CLI 0.7.45, HTML, CSS, project-local FFmpeg/FFprobe, HyperFrames-managed Chrome Headless Shell.

## Global Constraints

- Use simple Traditional Chinese copy understandable by non-programmers.
- Do not modify the main app `index.html`.
- Do not use Docker or optional local AI audio tools for this preview.
- Keep the first deliverable as a direction-confirmation composition, not final rendered video polish.

---

### Task 1: Create Preview Composition

**Files:**
- Create: `hyperframes/closing-report/index.html`
- Modify: `README.md`
- Modify: `progress.md`

**Interfaces:**
- Consumes: Approved storyboard from `docs/superpowers/specs/2026-07-09-closing-report-hyperframes-design.md`.
- Produces: A HyperFrames project directory that can be checked with `npx.cmd hyperframes lint hyperframes/closing-report`.

- [ ] **Step 1: Create the composition**

Create a 1920x1080 root with `data-composition-id="closing-report"` and six `class="clip"` timed scenes.

- [ ] **Step 2: Validate structure**

Run:

```powershell
npx.cmd hyperframes lint hyperframes/closing-report
```

Expected: command exits successfully with no errors.

- [ ] **Step 3: Capture preview frames**

Run:

```powershell
npx.cmd hyperframes snapshot hyperframes/closing-report --frames 6 --describe false
```

Expected: PNG snapshots are written under `hyperframes/closing-report/snapshots/`.

- [ ] **Step 4: Document status**

Update `README.md` with the preview commands and `progress.md` with the created composition path and verification outcome.

