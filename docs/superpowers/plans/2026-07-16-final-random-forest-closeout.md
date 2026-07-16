# Random Forest Final Close-Out Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the completed random-forest work with a clean Git tree, a final durable progress record, and fresh verification evidence.

**Architecture:** Restore the unrelated regenerated comparison PPTX to the current `main` version, append one final close-out section to `progress.md`, then run the complete project and artifact verification before committing only the progress record.

**Tech Stack:** Git, Markdown, Python unittest, Vitest, Vite, python-pptx, ZIP/OpenXML

## Global Constraints

- Preserve `data/model/random-forest-results.pptx` and every random-forest model artifact.
- Restore only `data/model/decision-tree-results-review.pptx` to HEAD because the user approved removing that unrelated binary difference.
- Do not regenerate model results or either PowerPoint during close-out.
- Do not add duplicate todo items; verify all relevant todo entries remain complete.
- Final `main` remains local-only and is not pushed.

---

### Task 1: Normalize Git Scope and Add the Close-Out Record

**Files:**
- Restore: `data/model/decision-tree-results-review.pptx`
- Modify: `progress.md`

- [ ] Restore the approved unrelated binary path with `git restore -- data/model/decision-tree-results-review.pptx` and verify it disappears from `git status --short`.
- [ ] Append `## 2026-07-16 Random-Forest Final Close-Out` to `progress.md` with final deliverables, 43.90% Accuracy, 40.81% Macro Recall, per-class/rare-class coverage, JSON-authoritative matrix generation, rerun command, artifact path/size/hash, verification checklist, and the fact that local `main` is not pushed.
- [ ] Run `rg -n "^- \[ \]" todo.md` and require no output.
- [ ] Run `git diff --check` and review the diff to ensure only `progress.md` changed.

### Task 2: Fresh Verification and Final Commit

**Files:**
- Modify only: `progress.md`

- [ ] Run `python -W error::ResourceWarning -m unittest discover -s tests -p 'test_*.py' -v`; require all tests pass.
- [ ] Run `npm.cmd test -- --run`; require all tests pass.
- [ ] Run `npm.cmd run build`; require exit 0; the existing large-chunk warning is acceptable.
- [ ] Independently verify `data/model/random-forest-results.pptx`: valid ZIP, two slides, 16:9, 43.90%, 40.81%, slide-2 matrix title and one image, 79,311 bytes, SHA-256 `6EE135805EECD82E1283F08DBBF43D0F50B8A06DBF483449DCCB2EA60B5D46F4`.
- [ ] Commit only `progress.md` with subject `docs: record random forest final close-out`.
- [ ] Verify `git status --short` is empty and report that `main` is ahead of `origin/main` but not pushed.

