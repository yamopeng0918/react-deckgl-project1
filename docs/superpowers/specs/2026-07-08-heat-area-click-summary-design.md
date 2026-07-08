# Heat Area Click Summary Design

## Goal

Add the remaining optional MVP interaction: clicking a heat area on the map shows a short summary for nearby filtered earthquake events.

## Scope

This is a local MVP enhancement for the existing mockup 6 data-lab React interface. It must not add new data sources, prediction logic, deployment behavior, or 3D/map rendering changes.

## Recommended Approach

Use map click coordinates to summarize nearby filtered events. `HeatmapLayer` does not return a single earthquake record, so the app should treat a click on the map background or heat area as a spatial query over the already-filtered dataset.

The query should:

- Use the clicked longitude/latitude.
- Find nearby filtered earthquake records within a small degree-based radius.
- Fall back to the nearest filtered records if no event is inside that radius.
- Produce a compact summary: event count, average magnitude, max magnitude, average depth, year range, and representative locations.

## UI Behavior

The existing selected-event panel should become capable of showing either:

- A selected earthquake event, from table row or point click.
- A selected heat-area summary, from map click.

Point and table selection should keep the current event-detail behavior. Map heat-area clicks should replace the detail body with heat-area facts and a clear panel note such as `Heat area`.

## Data Flow

The summary is derived only from `filteredRecords`, so it automatically respects the current year and magnitude filters. No new generated data file is needed.

## Testing

Add frontend tests that prove:

- The heatmap layer is pickable and has an `onClick` handler.
- Calling the heatmap click handler with coordinates updates the detail panel to heat-area summary content.
- Applying filters changes the set of records available to the heat-area summary.

## Non-Goals

- Exact geographic distance modeling.
- Persistent heat-area records in the processed dataset.
- A new right-side panel.
- Public deployment changes.
