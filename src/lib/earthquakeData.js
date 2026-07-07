export function getDatasetStats(records) {
  if (!records.length) {
    return {
      total: 0,
      minYear: 0,
      maxYear: 0,
      minMagnitude: 0,
      maxMagnitude: 0,
    };
  }

  const years = records.map((record) => record.year);
  const magnitudes = records.map((record) => record.magnitude);

  return {
    total: records.length,
    minYear: Math.min(...years),
    maxYear: Math.max(...years),
    minMagnitude: Math.min(...magnitudes),
    maxMagnitude: Math.max(...magnitudes),
  };
}

export function filterEarthquakes(records, filters) {
  return records.filter((record) => {
    return (
      record.year >= filters.yearMin &&
      record.year <= filters.yearMax &&
      record.magnitude >= filters.magnitudeMin &&
      record.magnitude <= filters.magnitudeMax
    );
  });
}

export function formatEarthquakeTime(value) {
  return value.replace("T", " ").slice(0, 16);
}
