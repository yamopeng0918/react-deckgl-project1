import { describe, expect, it } from "vitest";

import {
  filterEarthquakes,
  formatEarthquakeTime,
  getDatasetStats,
} from "./earthquakeData.js";

const records = [
  {
    id: "001",
    event_time: "1995-01-05T06:14:55",
    year: 1995,
    longitude: 121.7,
    latitude: 24.96,
    magnitude: 4.5,
    depth_km: 91.5,
    max_intensity: 2,
    location: "台北市地震站東偏南方",
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
    location: "嘉義縣政府東北東方",
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
    location: "花蓮縣政府東南方",
  },
];

describe("earthquake data helpers", () => {
  it("summarizes dataset year and magnitude bounds", () => {
    expect(getDatasetStats(records)).toEqual({
      total: 3,
      minYear: 1995,
      maxYear: 2025,
      minMagnitude: 4,
      maxMagnitude: 5.2,
    });
  });

  it("filters records by inclusive year and magnitude ranges", () => {
    const filtered = filterEarthquakes(records, {
      yearMin: 2024,
      yearMax: 2025,
      magnitudeMin: 4.1,
      magnitudeMax: 6,
    });

    expect(filtered.map((record) => record.id)).toEqual(["514"]);
  });

  it("formats ISO event time for table display", () => {
    expect(formatEarthquakeTime("2024-12-30T03:51:36")).toBe("2024-12-30 03:51");
  });
});
