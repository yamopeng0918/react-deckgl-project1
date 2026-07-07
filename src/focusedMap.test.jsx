import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ScatterplotLayer } from "@deck.gl/layers";

import App from "./App.jsx";

vi.mock("@deck.gl/react", () => ({
  default: ({ children }) => <div data-testid="deck-map">{children}</div>,
}));

vi.mock("@deck.gl/layers", () => ({
  ScatterplotLayer: vi.fn(),
}));

vi.mock("@deck.gl/aggregation-layers", () => ({
  HeatmapLayer: vi.fn(),
}));

vi.mock("react-map-gl/maplibre", () => ({
  default: () => <div data-testid="base-map" />,
}));

const dataset = [
  {
    id: "focus-1",
    event_time: "2025-01-01T00:00:00",
    year: 2025,
    longitude: 121,
    latitude: 23,
    magnitude: 4.5,
    depth_km: 10,
    max_intensity: 2,
    location: "Focused map location",
    source_file: "focus.csv",
  },
];

describe("focused map mode", () => {
  afterEach(() => {
    cleanup();
  });

  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => dataset,
    });
  });

  it("keeps the map in a sized panel and preserves the point layer", async () => {
    render(<App />);
    await screen.findByTestId("deck-map");

    const focusButton = screen
      .getAllByRole("button")
      .find((button) => button.textContent === "專注地圖");
    fireEvent.click(focusButton);

    expect(screen.getByTestId("deck-map").closest(".focus-map-panel")).not.toBeNull();

    const pointLayerProps = ScatterplotLayer.mock.calls.at(-1)[0];
    expect(pointLayerProps.data).toHaveLength(1);
    expect(pointLayerProps.visible).toBe(true);
  });

  it("forces earthquake points to be visible in focused map mode", async () => {
    render(<App />);
    await screen.findByTestId("deck-map");

    fireEvent.click(screen.getAllByRole("checkbox")[1]);

    const focusButton = screen
      .getAllByRole("button")
      .find((button) => button.textContent === "專注地圖");
    fireEvent.click(focusButton);

    const pointLayerProps = ScatterplotLayer.mock.calls.at(-1)[0];
    expect(pointLayerProps.visible).toBe(true);
    expect(pointLayerProps.radiusMinPixels).toBeGreaterThan(0);
    expect(pointLayerProps.parameters.depthTest).toBe(false);
  });
});
