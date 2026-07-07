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
    id: "range-1995",
    event_time: "1995-01-01T00:00:00",
    year: 1995,
    longitude: 121,
    latitude: 23,
    magnitude: 4.5,
    depth_km: 10,
    max_intensity: 2,
    location: "Old event",
    source_file: "range.csv",
  },
  {
    id: "range-2024",
    event_time: "2024-01-01T00:00:00",
    year: 2024,
    longitude: 121,
    latitude: 23,
    magnitude: 5.1,
    depth_km: 12,
    max_intensity: 3,
    location: "Recent event",
    source_file: "range.csv",
  },
];

describe("year range control", () => {
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

  it("combines year min and max into a single range control", async () => {
    render(<App />);
    await screen.findByTestId("deck-map");

    expect(screen.queryByLabelText("Year Min")).not.toBeInTheDocument();
    expect(screen.queryByLabelText("Year Max")).not.toBeInTheDocument();
    expect(screen.getByText("Year Range")).toBeInTheDocument();

    expect(document.querySelector(".dual-range")).not.toBeNull();
    expect(document.querySelector(".range-pair")).toBeNull();
    expect(screen.getAllByLabelText("Year range start")).toHaveLength(1);
    expect(screen.getAllByLabelText("Year range end")).toHaveLength(1);

    fireEvent.change(screen.getByLabelText("Year range start"), {
      target: { value: "2024" },
    });

    expect(await screen.findByText("1 筆資料")).toBeInTheDocument();
    expect(screen.queryByText("Old event")).not.toBeInTheDocument();
    expect(screen.getAllByText("Recent event").length).toBeGreaterThan(0);

    fireEvent.change(screen.getByLabelText("Year range end"), {
      target: { value: "1995" },
    });

    expect(await screen.findByText("1 筆資料")).toBeInTheDocument();
    expect(screen.getAllByText("Recent event").length).toBeGreaterThan(0);
  });

  it("moves the nearest year thumb when interacting with the shared track", async () => {
    render(<App />);
    await screen.findByTestId("deck-map");

    const track = document.querySelector(".dual-range");
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

    fireEvent.pointerDown(track, { clientX: 25, pointerId: 1 });

    expect(await screen.findByText("2002 - 2024")).toBeInTheDocument();
    expect(screen.queryByText("Old event")).not.toBeInTheDocument();
  });
});
