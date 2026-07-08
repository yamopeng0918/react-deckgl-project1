# Heat Area Click Summary Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add click summaries for heat areas by deriving nearby-event summaries from the currently filtered earthquake records.

**Architecture:** Keep the implementation inside the existing React app because map layers, selected state, and the detail panel already live in `src/App.jsx`. Add small pure helper functions in the same file for spatial querying and summary formatting so tests can drive behavior through the public UI and mocked deck.gl layer props.

**Tech Stack:** React 19, Vite, Vitest, Testing Library, deck.gl `HeatmapLayer`, deck.gl `ScatterplotLayer`.

## Global Constraints

- Do not add a new data source or generated data file.
- The summary must use `filteredRecords`, so year and magnitude filters affect it automatically.
- Keep existing point-click and table-row selected-event behavior.
- Keep the MVP local-app scope.
- Follow TDD: write and run the failing test before production code changes.

---

### Task 1: Heat Area Summary Interaction

**Files:**
- Modify: `src/App.test.jsx`
- Modify: `src/App.jsx`
- Modify: `todo.md`
- Modify: `progress.md`

**Interfaces:**
- Consumes: existing mocked `HeatmapLayer` constructor in `src/App.test.jsx`.
- Produces: `HeatmapLayer` props with `pickable: true` and `onClick({ coordinate })`.
- Produces: detail panel state that can render either an event record or a heat-area summary object.

- [ ] **Step 1: Write the failing test**

Add a test to `src/App.test.jsx` that imports `HeatmapLayer`, triggers the heatmap `onClick` prop with a coordinate near two filtered records, and expects the selected detail panel to show heat-area summary content:

```jsx
import { HeatmapLayer } from "@deck.gl/aggregation-layers";

it("shows a heat-area summary from nearby filtered events when the heatmap is clicked", async () => {
  render(<App />);
  await screen.findByText("3 蝑???);

  const heatmapProps = HeatmapLayer.mock.calls.at(-1)[0];
  expect(heatmapProps.pickable).toBe(true);

  heatmapProps.onClick({ coordinate: [121.69, 24] });

  expect(await screen.findByText("Heat area")).toBeInTheDocument();
  expect(screen.getByText("Nearby events")).toBeInTheDocument();
  expect(screen.getByText("2")).toBeInTheDocument();
  expect(screen.getByText("M 4.3")).toBeInTheDocument();
  expect(screen.getByText("M 4.5")).toBeInTheDocument();
  expect(screen.getByText("1995 - 2025")).toBeInTheDocument();
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm.cmd test -- --run src/App.test.jsx`

Expected: FAIL because `HeatmapLayer` currently has no `pickable` or `onClick` behavior and no heat-area summary UI exists.

- [ ] **Step 3: Write minimal implementation**

In `src/App.jsx`:

- Add selected summary state, for example `const [selectedSummary, setSelectedSummary] = useState(null);`.
- Clear `selectedSummary` when point or table selection picks an event.
- Add `buildHeatAreaSummary(records, coordinate)` that finds records near the click coordinate and computes:
  - `type: "heat-area"`
  - `count`
  - `averageMagnitude`
  - `maxMagnitude`
  - `averageDepth`
  - `yearMin`
  - `yearMax`
  - `locations`
- Add `pickable: true` and `onClick` to `HeatmapLayer`; the handler builds a summary from `filteredRecords` and stores it.
- Change the detail panel to render `HeatAreaDetails` when `selectedSummary` is present; otherwise render the existing `SelectedDetails`.

- [ ] **Step 4: Run focused tests to verify pass**

Run: `npm.cmd test -- --run src/App.test.jsx`

Expected: PASS.

- [ ] **Step 5: Run full verification**

Run:

```powershell
npm.cmd test -- --run
npm.cmd run build
python -m unittest tests.test_process_earthquakes -v
```

Expected:

- All frontend tests pass.
- Production build passes, with the existing large chunk warning acceptable.
- Python data processing tests pass.

- [ ] **Step 6: Update tracking docs**

Update `todo.md`:

```markdown
- [x] Add click summary for heat areas if time allows.
```

Update `progress.md` with:

- The heat-area click summary behavior.
- The tests and verification commands run.
- The remaining manual browser readability check, if still not manually verified.
