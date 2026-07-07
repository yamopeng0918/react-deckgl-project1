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
    id: "theme-1",
    event_time: "2025-01-01T00:00:00",
    year: 2025,
    longitude: 121,
    latitude: 23,
    magnitude: 4.5,
    depth_km: 10,
    max_intensity: 2,
    location: "Theme test location",
    source_file: "theme.csv",
  },
];

describe("theme mode", () => {
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

  it("toggles dark theme from the header and stores the preference", async () => {
    render(<App />);
    await screen.findByTestId("deck-map");

    expect(document.querySelector(".app-shell")).not.toHaveClass("theme-dark");

    fireEvent.click(screen.getByRole("button", { name: "Switch to dark theme" }));

    expect(document.querySelector(".app-shell")).toHaveClass("theme-dark");
    expect(localStorage.getItem("earthquake-theme")).toBe("dark");
    expect(screen.getByRole("button", { name: "Switch to light theme" })).toBeInTheDocument();
  });

  it("restores the saved dark theme on load", async () => {
    localStorage.setItem("earthquake-theme", "dark");

    render(<App />);
    await screen.findByTestId("deck-map");

    expect(document.querySelector(".app-shell")).toHaveClass("theme-dark");
    expect(screen.getByRole("button", { name: "Switch to light theme" })).toBeInTheDocument();
  });
});
