import DeckGL from "@deck.gl/react";
import { HeatmapLayer } from "@deck.gl/aggregation-layers";
import { ScatterplotLayer } from "@deck.gl/layers";
import BaseMap from "react-map-gl/maplibre";
import "maplibre-gl/dist/maplibre-gl.css";
import { useEffect, useMemo, useRef, useState } from "react";

import {
  filterEarthquakes,
  formatEarthquakeTime,
  getDatasetStats,
} from "./lib/earthquakeData.js";

const INITIAL_VIEW_STATE = {
  longitude: 121,
  latitude: 23.7,
  zoom: 6.6,
  minZoom: 5,
  maxZoom: 11,
  pitch: 0,
  bearing: 0,
};

const MAP_STYLE = {
  version: 8,
  sources: {
    osm: {
      type: "raster",
      tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
      tileSize: 256,
      attribution: "OpenStreetMap contributors",
    },
  },
  layers: [{ id: "osm", type: "raster", source: "osm" }],
};

const TABLE_ROW_LIMIT = 100;
const THEME_STORAGE_KEY = "earthquake-theme";
const HEAT_AREA_RADIUS_DEGREES = 1;
const HEAT_AREA_FALLBACK_LIMIT = 8;

function getInitialTheme() {
  if (typeof localStorage === "undefined") return "light";
  return localStorage.getItem(THEME_STORAGE_KEY) === "dark" ? "dark" : "light";
}

function getRecordKey(record) {
  return record.record_key ?? `${record.source_file}::${record.id}::${record.event_time}`;
}

function prepareRecords(data) {
  return data
    .map((record) => ({
      ...record,
      record_key: `${record.source_file}::${record.id}::${record.event_time}`,
    }))
    .sort((a, b) => b.event_time.localeCompare(a.event_time));
}

function defaultFilters(stats) {
  return {
    yearMin: stats.minYear,
    yearMax: stats.maxYear,
    magnitudeMin: Math.floor(stats.minMagnitude),
    magnitudeMax: Math.ceil(stats.maxMagnitude),
  };
}

function formatMagnitude(value) {
  return `M ${Number(value.toFixed(1))}`;
}

function buildHeatAreaSummary(records, coordinate) {
  if (!coordinate || records.length === 0) return null;
  const [longitude, latitude] = coordinate;
  const rankedRecords = records
    .map((record) => ({
      record,
      distance: Math.hypot(record.longitude - longitude, record.latitude - latitude),
    }))
    .sort((a, b) => a.distance - b.distance);
  const nearbyRecords = rankedRecords
    .filter(({ distance }) => distance <= HEAT_AREA_RADIUS_DEGREES)
    .map(({ record }) => record);
  const summaryRecords =
    nearbyRecords.length > 0
      ? nearbyRecords
      : rankedRecords.slice(0, HEAT_AREA_FALLBACK_LIMIT).map(({ record }) => record);

  if (summaryRecords.length === 0) return null;

  const totalMagnitude = summaryRecords.reduce((total, record) => total + record.magnitude, 0);
  const totalDepth = summaryRecords.reduce((total, record) => total + record.depth_km, 0);
  const years = summaryRecords.map((record) => record.year);
  const locations = [...new Set(summaryRecords.map((record) => record.location))].slice(0, 3);

  return {
    type: "heat-area",
    count: summaryRecords.length,
    averageMagnitude: totalMagnitude / summaryRecords.length,
    maxMagnitude: Math.max(...summaryRecords.map((record) => record.magnitude)),
    averageDepth: totalDepth / summaryRecords.length,
    yearMin: Math.min(...years),
    yearMax: Math.max(...years),
    locations,
  };
}

export default function App() {
  const [records, setRecords] = useState([]);
  const [loadState, setLoadState] = useState("loading");
  const [filters, setFilters] = useState(null);
  const [showHeatmap, setShowHeatmap] = useState(true);
  const [showPoints, setShowPoints] = useState(true);
  const [selectedRecord, setSelectedRecord] = useState(null);
  const [selectedSummary, setSelectedSummary] = useState(null);
  const [mapFocus, setMapFocus] = useState(false);
  const [theme, setTheme] = useState(getInitialTheme);

  useEffect(() => {
    let cancelled = false;

    fetch("/data/earthquakes.json")
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Failed to load earthquake data: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        if (cancelled) return;
        const preparedData = prepareRecords(data);
        const stats = getDatasetStats(preparedData);
        setRecords(preparedData);
        setFilters(defaultFilters(stats));
        setSelectedRecord(preparedData[0] ?? null);
        setLoadState("ready");
      })
      .catch(() => {
        if (!cancelled) setLoadState("error");
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const stats = useMemo(() => getDatasetStats(records), [records]);
  const activeFilters = filters ?? defaultFilters(stats);
  const filteredRecords = useMemo(
    () => filterEarthquakes(records, activeFilters),
    [records, activeFilters],
  );
  const visibleTableRecords = filteredRecords.slice(0, TABLE_ROW_LIMIT);
  const selectedKey = selectedRecord ? getRecordKey(selectedRecord) : null;
  const selected =
    filteredRecords.find((record) => getRecordKey(record) === selectedKey) ??
    filteredRecords[0] ??
    null;
  const yearlyCounts = useMemo(() => getYearlyCounts(filteredRecords), [filteredRecords]);

  const layers = useMemo(() => {
    const heatmap = new HeatmapLayer({
      id: "earthquake-heatmap",
      data: filteredRecords,
      getPosition: (record) => [record.longitude, record.latitude],
      getWeight: () => 1,
      radiusPixels: 44,
      intensity: 1.15,
      threshold: 0.03,
      visible: showHeatmap,
      pickable: true,
      onClick: ({ coordinate }) => {
        const summary = buildHeatAreaSummary(filteredRecords, coordinate);
        if (summary) setSelectedSummary(summary);
      },
    });

    const points = new ScatterplotLayer({
      id: "earthquake-points",
      data: filteredRecords,
      getPosition: (record) => [record.longitude, record.latitude],
      getRadius: (record) => Math.max(2200, record.magnitude * 900),
      getFillColor: mapFocus ? [166, 43, 55, 220] : [125, 38, 48, 175],
      getLineColor: [255, 255, 255, 235],
      lineWidthMinPixels: 1,
      radiusMinPixels: mapFocus ? 4 : 2,
      radiusMaxPixels: mapFocus ? 22 : 16,
      parameters: { depthTest: false },
      pickable: true,
      visible: mapFocus || showPoints,
      onClick: ({ object }) => {
        if (object) {
          setSelectedRecord(object);
          setSelectedSummary(null);
        }
      },
    });

    return [heatmap, points];
  }, [filteredRecords, mapFocus, showHeatmap, showPoints]);

  function selectHeatArea(coordinate) {
    const summary = buildHeatAreaSummary(filteredRecords, coordinate);
    if (summary) setSelectedSummary(summary);
  }

  function updateYearRange(name, value) {
    setFilters((current) => {
      const numericValue = Number(value);
      if (name === "yearMin") {
        return {
          ...current,
          yearMin: Math.min(numericValue, current.yearMax),
        };
      }
      return {
        ...current,
        yearMax: Math.max(numericValue, current.yearMin),
      };
    });
  }

  function updateMagnitudeRange(name, value) {
    setFilters((current) => {
      const numericValue = Number(value);
      if (name === "magnitudeMin") {
        return {
          ...current,
          magnitudeMin: Math.min(numericValue, current.magnitudeMax),
        };
      }
      return {
        ...current,
        magnitudeMax: Math.max(numericValue, current.magnitudeMin),
      };
    });
  }

  function toggleTheme() {
    setTheme((current) => {
      const nextTheme = current === "dark" ? "light" : "dark";
      localStorage.setItem(THEME_STORAGE_KEY, nextTheme);
      return nextTheme;
    });
  }

  function selectRecord(record) {
    setSelectedRecord(record);
    setSelectedSummary(null);
  }

  if (loadState === "loading") {
    return <div className="boot">資料載入中</div>;
  }

  if (loadState === "error") {
    return <div className="boot">資料載入失敗</div>;
  }

  if (mapFocus) {
    return (
      <div className={`app-shell map-focus ${theme === "dark" ? "theme-dark" : ""}`}>
        <AppHeader
          count={filteredRecords.length}
          mapFocus={mapFocus}
          onToggleFocus={() => setMapFocus(false)}
          theme={theme}
          onToggleTheme={toggleTheme}
        />
        <section className="map-panel focus-map-panel">
          <MapPanel layers={layers} selected={selected} onMapClick={selectHeatArea} />
        </section>
      </div>
    );
  }

  return (
    <div className={`app-shell data-lab-shell ${theme === "dark" ? "theme-dark" : ""}`}>
      <AppHeader
        count={filteredRecords.length}
        mapFocus={mapFocus}
        onToggleFocus={() => setMapFocus(true)}
        theme={theme}
        onToggleTheme={toggleTheme}
      />

      <section className="filter-row" aria-label="篩選列">
        <DualRangeControl
          label="Year Range"
          className="year-range-control"
          startLabel="Year range start"
          endLabel="Year range end"
          startName="yearMin"
          endName="yearMax"
          startValue={activeFilters.yearMin}
          endValue={activeFilters.yearMax}
          min={stats.minYear}
          max={stats.maxYear}
          step={1}
          onChange={updateYearRange}
        />
        <DualRangeControl
          label="Magnitude Range"
          className="magnitude-range-control"
          startLabel="Magnitude range start"
          endLabel="Magnitude range end"
          startName="magnitudeMin"
          endName="magnitudeMax"
          startValue={activeFilters.magnitudeMin}
          endValue={activeFilters.magnitudeMax}
          min={Math.floor(stats.minMagnitude)}
          max={Math.ceil(stats.maxMagnitude)}
          step={0.1}
          formatValue={(value) => `M ${value}`}
          onChange={updateMagnitudeRange}
        />
        <div className="control layer-control">
          <span>Layer</span>
          <strong>{showHeatmap && showPoints ? "熱區 + 點位" : "自訂圖層"}</strong>
          <div className="mini-toggles">
            <LayerToggle
              label="熱區"
              checked={showHeatmap}
              onChange={() => setShowHeatmap((value) => !value)}
            />
            <LayerToggle
              label="點位"
              checked={showPoints}
              onChange={() => setShowPoints((value) => !value)}
            />
          </div>
        </div>
      </section>

      <main className="workspace">
        <section className="left-stack">
          <section className="table-panel">
            <PanelHead
              title="地震事件資料表"
              note={`顯示最新 ${visibleTableRecords.length.toLocaleString()} / ${filteredRecords.length.toLocaleString()} 筆`}
            />
            <EventTable
              records={visibleTableRecords}
              selectedKey={selected ? getRecordKey(selected) : null}
              onSelect={selectRecord}
            />
          </section>

          <section className="chart-panel">
            <PanelHead title="年份事件量" note="目前篩選結果" />
            <YearlyBars counts={yearlyCounts} />
          </section>
        </section>

        <section className="right-stack">
          <section className="map-panel">
            <PanelHead title="同步地圖" note="熱區與選取事件" />
            <MapPanel layers={layers} selected={selected} onMapClick={selectHeatArea} />
          </section>

          <section className="detail-panel">
            <PanelHead title="選取事件摘要" note={selected ? `ID ${selected.id}` : "尚未選取"} />
            {selectedSummary ? (
              <HeatAreaDetails summary={selectedSummary} />
            ) : selected ? (
              <SelectedDetails record={selected} />
            ) : null}
          </section>
        </section>
      </main>
    </div>
  );
}

function AppHeader({ count, mapFocus, onToggleFocus, theme, onToggleTheme }) {
  return (
    <header className="app-header">
      <h1>台灣地震熱區探索器</h1>
      <div className="status">
        <span>{count.toLocaleString()} 筆資料</span>
        <button
          type="button"
          className="theme-toggle"
          aria-label={theme === "dark" ? "Switch to light theme" : "Switch to dark theme"}
          onClick={onToggleTheme}
        >
          {theme === "dark" ? "Light" : "Dark"}
        </button>
        <button type="button" onClick={onToggleFocus}>
          {mapFocus ? "返回工作台" : "專注地圖"}
        </button>
      </div>
    </header>
  );
}

function DualRangeControl({
  label,
  className,
  startLabel,
  endLabel,
  startName,
  endName,
  startValue,
  endValue,
  min,
  max,
  step,
  formatValue = (value) => value,
  onChange,
}) {
  const trackRef = useRef(null);
  const activeThumbRef = useRef(null);
  const span = Math.max(max - min, 1);
  const startPercent = ((startValue - min) / span) * 100;
  const endPercent = ((endValue - min) / span) * 100;
  const stepText = String(step);
  const decimals = stepText.includes(".") ? stepText.split(".")[1].length : 0;

  function normalizeValue(value) {
    const steppedValue = Math.round((value - min) / step) * step + min;
    const clampedValue = Math.min(max, Math.max(min, steppedValue));
    return Number(clampedValue.toFixed(decimals));
  }

  function getValueFromPointer(clientX) {
    const rect = trackRef.current?.getBoundingClientRect();
    if (!rect || rect.width <= 0) return startValue;

    const ratio = Math.min(1, Math.max(0, (clientX - rect.left) / rect.width));
    return normalizeValue(min + ratio * span);
  }

  function getNearestThumb(value) {
    return Math.abs(value - startValue) <= Math.abs(value - endValue) ? startName : endName;
  }

  function updateThumbFromPointer(event, thumb = activeThumbRef.current) {
    if (!thumb) return;
    onChange(thumb, getValueFromPointer(event.clientX));
  }

  function handlePointerDown(event) {
    const nextValue = getValueFromPointer(event.clientX);
    const thumb = getNearestThumb(nextValue);
    activeThumbRef.current = thumb;
    event.currentTarget.setPointerCapture?.(event.pointerId);
    onChange(thumb, nextValue);
  }

  function handlePointerMove(event) {
    updateThumbFromPointer(event);
  }

  function handlePointerEnd(event) {
    activeThumbRef.current = null;
    event.currentTarget.releasePointerCapture?.(event.pointerId);
  }

  return (
    <div className={`control ${className}`}>
      <span>{label}</span>
      <strong>
        {formatValue(startValue)} - {formatValue(endValue)}
      </strong>
      <div
        className="dual-range"
        ref={trackRef}
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={handlePointerEnd}
        onPointerCancel={handlePointerEnd}
        style={{
          "--range-start": `${startPercent}%`,
          "--range-end": `${endPercent}%`,
        }}
      >
        <input
          aria-label={startLabel}
          type="range"
          min={min}
          max={max}
          step={step}
          value={startValue}
          onChange={(event) => onChange(startName, event.target.value)}
        />
        <input
          aria-label={endLabel}
          type="range"
          min={min}
          max={max}
          step={step}
          value={endValue}
          onChange={(event) => onChange(endName, event.target.value)}
        />
      </div>
    </div>
  );
}

function LayerToggle({ label, checked, onChange }) {
  return (
    <label className="mini-toggle">
      <span>{label}</span>
      <input type="checkbox" checked={checked} onChange={onChange} />
    </label>
  );
}

function PanelHead({ title, note }) {
  return (
    <div className="panel-head">
      <strong>{title}</strong>
      <span>{note}</span>
    </div>
  );
}

function MapPanel({ layers, selected, onMapClick }) {
  function handleMapClick(info) {
    if (info?.object?.event_time) return;
    if (info?.coordinate) onMapClick(info.coordinate);
  }

  return (
    <div className="map-canvas" aria-label="台灣地震熱區地圖">
      <DeckGL
        controller
        initialViewState={INITIAL_VIEW_STATE}
        layers={layers}
        onClick={handleMapClick}
        getTooltip={({ object }) =>
          object
            ? {
                text: `${formatEarthquakeTime(object.event_time)}\nM ${object.magnitude} / ${object.depth_km} km\n${object.location}`,
              }
            : null
        }
      >
        <BaseMap mapStyle={MAP_STYLE} reuseMaps />
      </DeckGL>
      {selected ? (
        <div className="map-selection">
          <span>Selected</span>
          <strong>M {selected.magnitude}</strong>
          <small>{selected.location}</small>
        </div>
      ) : null}
    </div>
  );
}

function EventTable({ records, selectedKey, onSelect }) {
  return (
    <table>
      <thead>
        <tr>
          <th>時間</th>
          <th>震級</th>
          <th>深度</th>
          <th>最大震度</th>
          <th>經度</th>
          <th>緯度</th>
          <th>位置</th>
        </tr>
      </thead>
      <tbody>
        {records.map((record) => (
          <tr
            className={getRecordKey(record) === selectedKey ? "selected-row" : ""}
            key={getRecordKey(record)}
            onClick={() => onSelect(record)}
          >
            <td>{formatEarthquakeTime(record.event_time)}</td>
            <td>
              <span className="magnitude-badge">M {record.magnitude}</span>
            </td>
            <td>{record.depth_km} km</td>
            <td>{record.max_intensity}</td>
            <td>{record.longitude}</td>
            <td>{record.latitude}</td>
            <td>{record.location}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function YearlyBars({ counts }) {
  const maxCount = Math.max(...counts.map(({ count }) => count), 1);
  const firstYear = counts[0]?.year ?? "";
  const middleYear = counts[Math.floor((counts.length - 1) / 2)]?.year ?? "";
  const lastYear = counts.at(-1)?.year ?? "";

  return (
    <>
      <div
        className="bars"
        aria-label="年份事件量圖"
        style={{ "--bar-count": counts.length }}
      >
        {counts.map(({ year, count }) => (
          <span
            className={`bar${count === 0 ? " empty-bar" : ""}`}
            key={year}
            style={{ height: count === 0 ? "2px" : `${Math.max(12, (count / maxCount) * 100)}%` }}
            title={`${year}: ${count} 筆`}
          />
        ))}
      </div>
      <div className="axis">
        <span>{firstYear}</span>
        <span>{middleYear}</span>
        <span>{lastYear}</span>
      </div>
    </>
  );
}

function SelectedDetails({ record }) {
  return (
    <div className="detail-body">
      <div className="fact">
        <span>震級</span>
        <strong>M {record.magnitude}</strong>
      </div>
      <div className="fact">
        <span>深度</span>
        <strong>{record.depth_km} km</strong>
      </div>
      <div className="fact">
        <span>最大震度</span>
        <strong>{record.max_intensity}</strong>
      </div>
      <div className="fact">
        <span>時間</span>
        <strong>{formatEarthquakeTime(record.event_time)}</strong>
      </div>
      <div className="fact wide">
        <span>位置</span>
        <strong>{record.location}，目前篩選結果中的選取事件</strong>
      </div>
      <div className="fact wide">
        <span>來源</span>
        <strong>{record.source_file}</strong>
      </div>
    </div>
  );
}

function HeatAreaDetails({ summary }) {
  return (
    <div className="detail-body">
      <div className="fact">
        <span>Heat area</span>
        <strong>Summary</strong>
      </div>
      <div className="fact">
        <span>Nearby events</span>
        <strong>{summary.count}</strong>
      </div>
      <div className="fact">
        <span>Average magnitude</span>
        <strong>{formatMagnitude(summary.averageMagnitude)}</strong>
      </div>
      <div className="fact">
        <span>Max magnitude</span>
        <strong>{formatMagnitude(summary.maxMagnitude)}</strong>
      </div>
      <div className="fact">
        <span>Average depth</span>
        <strong>{summary.averageDepth.toFixed(1)} km</strong>
      </div>
      <div className="fact">
        <span>Years</span>
        <strong>
          {summary.yearMin} - {summary.yearMax}
        </strong>
      </div>
      <div className="fact wide">
        <span>Representative locations</span>
        <strong>{summary.locations.join(" / ")}</strong>
      </div>
    </div>
  );
}

function getYearlyCounts(records) {
  if (records.length === 0) return [];
  const years = records.map((record) => record.year);
  const minYear = Math.min(...years);
  const maxYear = Math.max(...years);
  const countsByYear = new Map();
  records.forEach((record) => {
    countsByYear.set(record.year, (countsByYear.get(record.year) ?? 0) + 1);
  });

  return Array.from({ length: maxYear - minYear + 1 }, (_, index) => {
    const year = minYear + index;
    return {
      year,
      count: countsByYear.get(year) ?? 0,
    };
  });
}
