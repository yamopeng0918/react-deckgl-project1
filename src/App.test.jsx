import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { HeatmapLayer } from "@deck.gl/aggregation-layers";
import DeckGL from "@deck.gl/react";

import App from "./App.jsx";

vi.mock("@deck.gl/react", () => ({
  default: vi.fn(({ children }) => <div data-testid="deck-map">{children}</div>),
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
    id: "001",
    event_time: "1995-01-05T06:14:55",
    year: 1995,
    longitude: 121.7,
    latitude: 24.96,
    magnitude: 4.5,
    depth_km: 91.5,
    max_intensity: 2,
    location: "Yilan offshore",
    source_file: "earthquakes_1995.csv",
  },
  {
    id: "514",
    event_time: "2024-12-30T03:51:36",
    year: 2024,
    longitude: 120.685,
    latitude: 23.5383,
    magnitude: 5.2,
    depth_km: 15.1,
    max_intensity: 4,
    location: "Hualien offshore",
    source_file: "earthquakes_2024.csv",
  },
  {
    id: "2025-01",
    event_time: "2025-01-31T23:19:09",
    year: 2025,
    longitude: 121.684,
    latitude: 23.9102,
    magnitude: 4,
    depth_km: 52.1,
    max_intensity: 1,
    location: "Taitung offshore",
    source_file: "2025/earthquakes_202501.csv",
  },
];

function makeRecord(index) {
  const year = 2025 - (index % 3);
  const month = String((index % 12) + 1).padStart(2, "0");
  const day = String((index % 28) + 1).padStart(2, "0");

  return {
    id: `large-${index}`,
    event_time: `${year}-${month}-${day}T12:00:00`,
    year,
    longitude: 121 + (index % 10) * 0.01,
    latitude: 23 + (index % 10) * 0.01,
    magnitude: 4 + (index % 20) / 10,
    depth_km: 10 + index,
    max_intensity: index % 7,
    location: `Large dataset location ${index}`,
    source_file: `large_${year}.csv`,
  };
}

describe("App", () => {
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

  it("loads the mockup 6 data lab layout", async () => {
    render(<App />);

    expect(await screen.findByText("台灣地震熱區探索器")).toBeInTheDocument();
    expect(screen.getByText("3 筆資料")).toBeInTheDocument();
    expect(screen.getByText("地震事件資料表")).toBeInTheDocument();
    expect(screen.getByText("同步地圖")).toBeInTheDocument();
    expect(screen.getByText("選取事件摘要")).toBeInTheDocument();
    expect(screen.getByText("年份事件量")).toBeInTheDocument();
    expect(screen.getByLabelText("年份事件量圖")).toBeInTheDocument();
    expect(screen.getByText("1995")).toBeInTheDocument();
    expect(screen.getByText("2025")).toBeInTheDocument();
    expect(screen.getByTestId("deck-map")).toBeInTheDocument();
  });

  it("renders zero-count yearly bars differently from one-count yearly bars", async () => {
    render(<App />);
    await screen.findByText("Yilan offshore");

    const chart = screen.getByLabelText("年份事件量圖");
    const zeroCountBar = chart.querySelector('[title^="1996: 0"]');
    const oneCountBar = chart.querySelector('[title^="1995: 1"]');

    expect(zeroCountBar).toHaveClass("empty-bar");
    expect(zeroCountBar).toHaveStyle({ height: "2px" });
    expect(oneCountBar).not.toHaveClass("empty-bar");
    expect(oneCountBar).not.toHaveStyle({ height: "2px" });
  });

  it("limits visible table rows for large datasets to keep initial load responsive", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => Array.from({ length: 300 }, (_, index) => makeRecord(index)),
    });

    render(<App />);

    expect(await screen.findByText("300 筆資料")).toBeInTheDocument();
    expect(screen.getByText("顯示最新 100 / 300 筆")).toBeInTheDocument();
    expect(screen.getAllByRole("row")).toHaveLength(101);
  });

  it("updates the filtered count from the top filter row", async () => {
    render(<App />);
    await screen.findByText("3 筆資料");

    fireEvent.change(screen.getByLabelText("Year range start"), { target: { value: "2024" } });

    expect(await screen.findByText("2 筆資料")).toBeInTheDocument();
    expect(screen.getAllByText("Hualien offshore").length).toBeGreaterThan(0);
    expect(screen.queryByText("Yilan offshore")).not.toBeInTheDocument();
  });

  it("syncs table row selection into the selected event summary", async () => {
    render(<App />);
    await screen.findByText("3 筆資料");

    fireEvent.click(screen.getByText("Hualien offshore"));

    expect(screen.getByText("ID 514")).toBeInTheDocument();
    expect(screen.getAllByText("M 5.2").length).toBeGreaterThan(0);
    expect(screen.getAllByText("15.1 km").length).toBeGreaterThan(0);
  });

  it("shows a heat-area summary from nearby filtered events when the heatmap is clicked", async () => {
    render(<App />);
    await screen.findByText("Yilan offshore");

    const heatmapProps = HeatmapLayer.mock.calls.at(-1)[0];
    expect(heatmapProps.pickable).toBe(true);

    heatmapProps.onClick({ coordinate: [121.69, 24] });

    expect(await screen.findByText("Heat area")).toBeInTheDocument();
    expect(screen.getByText("Nearby events")).toBeInTheDocument();
    expect(screen.getByText("2", { selector: ".fact strong" })).toBeInTheDocument();
    expect(screen.getByText("M 4.3", { selector: ".fact strong" })).toBeInTheDocument();
    expect(screen.getByText("M 4.5", { selector: ".fact strong" })).toBeInTheDocument();
    expect(screen.getByText("1995 - 2025", { selector: ".fact strong" })).toBeInTheDocument();
  });

  it("shows a heat-area summary from a direct map click coordinate", async () => {
    render(<App />);
    await screen.findByText("Yilan offshore");

    const deckProps = DeckGL.mock.calls.at(-1)[0];
    expect(deckProps.onClick).toEqual(expect.any(Function));

    deckProps.onClick({ coordinate: [121.69, 24] });

    expect(await screen.findByText("Heat area")).toBeInTheDocument();
    expect(screen.getByText("Nearby events")).toBeInTheDocument();
    expect(screen.getByText("2", { selector: ".fact strong" })).toBeInTheDocument();
  });

  it("uses a stable record identity when duplicate source ids exist", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => [
        {
          id: "same-id",
          event_time: "2024-01-01T00:00:00",
          year: 2024,
          longitude: 121,
          latitude: 23,
          magnitude: 4.1,
          depth_km: 10,
          max_intensity: 2,
          location: "Duplicate A",
          source_file: "source_a.csv",
        },
        {
          id: "same-id",
          event_time: "2025-01-01T00:00:00",
          year: 2025,
          longitude: 122,
          latitude: 24,
          magnitude: 5.9,
          depth_km: 99,
          max_intensity: 5,
          location: "Duplicate B",
          source_file: "source_b.csv",
        },
      ],
    });

    render(<App />);
    await screen.findByText("Duplicate A");

    fireEvent.click(screen.getByText("Duplicate A"));

    expect(screen.getByText("source_a.csv")).toBeInTheDocument();
    expect(screen.getAllByText("M 4.1").length).toBeGreaterThan(0);
  });

  it("toggles a focused map mode from the data lab header", async () => {
    render(<App />);
    await screen.findByText("3 筆資料");

    fireEvent.click(screen.getByRole("button", { name: "專注地圖" }));

    expect(screen.queryByText("地震事件資料表")).not.toBeInTheDocument();
    expect(screen.queryByLabelText("Year Min")).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: "返回工作台" })).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "返回工作台" }));

    expect(await screen.findByText("地震事件資料表")).toBeInTheDocument();
  });
});
