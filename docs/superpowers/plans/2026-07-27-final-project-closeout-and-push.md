# Final Project Close-Out and Push Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Freshly verify the completed project, record final deliverables and evidence, then safely synchronize local `main` to `origin/main`.

**Architecture:** The close-out runs directly on `main` because the requested outcome is to synchronize that branch. Task 1 performs all read-only verification and commits a pre-push close-out record; Task 2 fetches and checks remote ancestry, pushes normally, then records and pushes the verified synchronization state without placeholders.

**Tech Stack:** Python unittest, Vitest, Vite, python-pptx, ZIP/OpenXML, Git.

## Global Constraints

- Do not add features, redeploy Vercel, or create a Git tag.
- Do not add, modify, delete, stage, or commit `決策樹簡報小白解釋.txt`.
- Do not force-push.
- If any test, build, PowerPoint validation, remote ancestry check, or push fails, stop and report the actual failure.
- Do not claim a push succeeded before it has succeeded.
- Final local `main` and `origin/main` must point to the same commit.

---

### Task 1: Fresh verification and pre-push close-out record

**Files:**
- Modify: `progress.md`
- Modify: `todo.md`

**Interfaces:**
- Consumes: current tracked project, three final random-forest PowerPoints, local ignored fitted model.
- Produces: a committed close-out record containing fresh verification evidence and a final todo section with push left unchecked.

- [ ] **Step 1: Confirm clean tracked scope**

```powershell
git status --short --branch
git diff --check
```

Expected: no tracked changes; only the existing untracked `決策樹簡報小白解釋.txt`; local `main` may be ahead of `origin/main`.

- [ ] **Step 2: Run the full Python suite**

```powershell
python -W error::ResourceWarning -m unittest discover -s tests -p 'test_*.py' -v
```

Expected: all tests pass with no `ResourceWarning`.

- [ ] **Step 3: Run Vitest and the production build**

```powershell
npm.cmd test -- --run
npm.cmd run build
```

Expected: Vitest passes; Vite build succeeds with only the accepted large-chunk warning.

- [ ] **Step 4: Validate all three PowerPoints independently**

Run a read-only Python assertion script that opens each file with ZIP and `python-pptx`:

```python
expected = {
    "data/model/random-forest-results.pptx": 2,
    "data/model/random-forest-three-level-explainer.pptx": 1,
    "data/model/random-forest-feature-importance.pptx": 1,
}
```

For each path, assert file size > 0, `ZipFile.testzip()` is `None`, slide count matches, and `slide_width / slide_height` is within 0.01 of `16 / 9`. Record size and SHA-256.

- [ ] **Step 5: Update `progress.md` with pre-push evidence**

Append `## 2026-07-27 Final Project Close-Out` containing:

- completed map MVP, 1995–2026 data pipeline, model comparison, and three PowerPoints;
- 16,691 exported records;
- decision tree accuracy 28.33% / macro recall 30.43%;
- random forest accuracy 43.90% / macro recall 40.81%;
- ranked feature importance values and spatial/temporal totals;
- all three artifact paths, slide counts, measured sizes, and SHA-256 values;
- exact fresh Python, Vitest, build, and PowerPoint verification results;
- statement `Remote synchronization is pending the verified push step.`

- [ ] **Step 6: Update `todo.md` without claiming push success**

Add:

```markdown
## Final Project Close-Out

- [x] Rerun the complete Python test suite.
- [x] Rerun the complete Vitest suite.
- [x] Rerun the production build.
- [x] Validate the three final random-forest PowerPoints.
- [x] Record final deliverables, metrics, insights, hashes, and limitations.
- [ ] Push `main` to `origin/main` and verify synchronization.
```

- [ ] **Step 7: Review and commit the pre-push record**

```powershell
git diff --check
git diff -- progress.md todo.md
git status --short
git add -- progress.md todo.md
git commit -m "docs: record final project closeout"
```

Expected: commit contains only `progress.md` and `todo.md`; the user text file remains untracked.

### Task 2: Safe remote synchronization and final record

**Files:**
- Modify: `progress.md`
- Modify: `todo.md`

**Interfaces:**
- Consumes: Task 1 close-out commit on local `main`.
- Produces: synchronized `main`/`origin/main` refs and a final synchronization record committed and pushed.

- [ ] **Step 1: Fetch and verify remote ancestry**

```powershell
git fetch origin main
git rev-parse main
git rev-parse origin/main
git merge-base --is-ancestor origin/main main
```

Expected: ancestry command exits 0. If it exits nonzero, stop; do not merge, rebase, or push automatically.

- [ ] **Step 2: Push the close-out commit normally**

```powershell
git push origin main
```

Expected: normal fast-forward push succeeds.

- [ ] **Step 3: Verify first synchronization**

```powershell
git fetch origin main
git rev-parse main
git rev-parse origin/main
```

Expected: both refs are identical.

- [ ] **Step 4: Record actual synchronization**

Append to the close-out section in `progress.md`:

- the Task 1 close-out commit SHA;
- first push success;
- fetched proof that `main` and `origin/main` matched that SHA;
- statement that a final documentation commit will record the completed synchronization.

Change the final `todo.md` item to:

```markdown
- [x] Push `main` to `origin/main` and verify synchronization.
```

- [ ] **Step 5: Commit the synchronization record**

```powershell
git diff --check
git add -- progress.md todo.md
git commit -m "docs: confirm origin main synchronization"
```

Record the new commit SHA from `git rev-parse HEAD`.

- [ ] **Step 6: Push and verify the final commit**

```powershell
git push origin main
git fetch origin main
git rev-parse main
git rev-parse origin/main
```

Expected: push succeeds and both refs point to the final documentation commit.

- [ ] **Step 7: Final scope check**

```powershell
git status --short --branch
git log -3 --oneline
```

Expected: `main...origin/main` with no ahead/behind count; only `決策樹簡報小白解釋.txt` remains untracked.

