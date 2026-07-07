import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

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
    id: "mag-low",
    event_time: "2024-01-01T00:00:00",
    year: 2024,
    longitude: 121,
    latitude: 23,
    magnitude: 3.2,
    depth_km: 10,
    max_intensity: 2,
    location: "Low magnitude event",
    source_file: "magnitude.csv",
  },
  {
    id: "mag-mid",
    event_time: "2024-02-01T00:00:00",
    year: 2024,
    longitude: 121,
    latitude: 23,
    magnitude: 4.2,
    depth_km: 12,
    max_intensity: 3,
    location: "Mid magnitude event",
    source_file: "magnitude.csv",
  },
  {
    id: "mag-high",
    event_time: "2024-03-01T00:00:00",
    year: 2024,
    longitude: 121,
    latitude: 23,
    magnitude: 5.8,
    depth_km: 14,
    max_intensity: 4,
    location: "High magnitude event",
    source_file: "magnitude.csv",
  },
];

describe("magnitude range control", () => {
  afterEach(() => {
    cleanup();
  });

  beforeEach(() => {
    localStorage.clear();
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => dataset,
    });
  });

  it("combines magnitude min and max into a single range control", async () => {
    render(<App />);
    await screen.findByTestId("deck-map");

    expect(screen.queryByLabelText("Magnitude Min")).not.toBeInTheDocument();
    expect(screen.queryByLabelText("Magnitude Max")).not.toBeInTheDocument();
    expect(screen.getByText("Magnitude Range")).toBeInTheDocument();
    expect(screen.getAllByLabelText("Magnitude range start")).toHaveLength(1);
    expect(screen.getAllByLabelText("Magnitude range end")).toHaveLength(1);

    fireEvent.change(screen.getByLabelText("Magnitude range start"), {
      target: { value: "5" },
    });

    expect(await screen.findByText("1 筆資料")).toBeInTheDocument();
    expect(screen.queryByText("Low magnitude event")).not.toBeInTheDocument();
    expect(screen.queryByText("Mid magnitude event")).not.toBeInTheDocument();
    expect(screen.getAllByText("High magnitude event").length).toBeGreaterThan(0);
  });

  it("moves the nearest magnitude thumb when interacting with the shared track", async () => {
    render(<App />);
    await screen.findByTestId("deck-map");

    const track = document.querySelector(".magnitude-range-control .dual-range");
    vi.spyOn(track, "getBoundingClientRect").mockReturnValue({
      left: 0,
      right: 100,
      top: 0,
      bottom: 28,
      width: 100,
      height: 28,
      x: 0,
      y: 0,
      toJSON: () => {},
    });

    fireEvent.pointerDown(track, { clientX: 67, pointerId: 1 });

    expect(await screen.findByText("M 3 - M 5")).toBeInTheDocument();
    expect(screen.queryByText("High magnitude event")).not.toBeInTheDocument();
    expect(screen.getAllByText("Low magnitude event").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Mid magnitude event").length).toBeGreaterThan(0);
  });
});
