import csv
import json
from datetime import datetime
from pathlib import Path


SOURCE_DIR = Path("(彭元懋)_台灣地震活動彙整")
JSON_OUTPUT = Path("public/data/earthquakes.json")
CSV_OUTPUT = Path("data/processed/earthquakes.csv")

SOURCE_COLUMNS = ["編號", "地震時間", "經度", "緯度", "規模", "深度", "最大震度", "位置"]
OUTPUT_COLUMNS = [
    "id",
    "event_time",
    "year",
    "longitude",
    "latitude",
    "magnitude",
    "depth_km",
    "max_intensity",
    "location",
    "source_file",
]


def process_dataset(source_dir, json_output, csv_output):
    source_dir = Path(source_dir)
    json_output = Path(json_output)
    csv_output = Path(csv_output)

    records = []
    total_rows = 0
    invalid_rows = 0
    source_files = list(discover_csv_files(source_dir))

    for source_file in source_files:
        for row in read_source_rows(source_file):
            total_rows += 1
            record = normalize_row(row, source_file, source_dir)
            if record is None:
                invalid_rows += 1
                continue
            records.append(record)

    records.sort(key=lambda record: (record["event_time"], record["source_file"], record["id"]))
    write_json(json_output, records)
    write_csv(csv_output, records)

    return {
        "source_files": len(source_files),
        "total_input_rows": total_rows,
        "exported_rows": len(records),
        "invalid_rows": invalid_rows,
        "included_years": sorted({record["year"] for record in records}),
        "json_output": str(json_output),
        "csv_output": str(csv_output),
    }


def discover_csv_files(source_dir):
    if not source_dir.exists():
        raise FileNotFoundError(f"Source data directory not found: {source_dir}")
    return sorted(path for path in source_dir.rglob("*.csv") if path.is_file())


def read_source_rows(source_file):
    with source_file.open(newline="", encoding="cp950") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames != SOURCE_COLUMNS:
            raise ValueError(f"Unexpected columns in {source_file}: {reader.fieldnames}")
        yield from reader


def normalize_row(row, source_file, source_dir):
    event_time = parse_event_time(row.get("地震時間"))
    longitude = parse_float(row.get("經度"))
    latitude = parse_float(row.get("緯度"))
    magnitude = parse_float(row.get("規模"))
    depth_km = parse_float(row.get("深度"))

    if event_time is None:
        return None
    if not valid_longitude(longitude) or not valid_latitude(latitude):
        return None
    if magnitude is None or depth_km is None:
        return None

    return {
        "id": clean_text(row.get("編號")),
        "event_time": event_time.isoformat(),
        "year": event_time.year,
        "longitude": longitude,
        "latitude": latitude,
        "magnitude": magnitude,
        "depth_km": depth_km,
        "max_intensity": parse_int_or_text(row.get("最大震度")),
        "location": clean_text(row.get("位置")),
        "source_file": Path(source_file).relative_to(source_dir).as_posix(),
    }


def parse_event_time(value):
    text = clean_text(value)
    if not text:
        return None
    try:
        return datetime.strptime(text, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None


def parse_float(value):
    text = clean_text(value)
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def parse_int_or_text(value):
    text = clean_text(value)
    if not text:
        return ""
    try:
        return int(text)
    except ValueError:
        return text


def clean_text(value):
    return "" if value is None else str(value).strip()


def valid_longitude(value):
    return value is not None and 115 <= value <= 126.5


def valid_latitude(value):
    return value is not None and 18 <= value <= 27


def write_json(output_path, records):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(records, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_csv(output_path, records):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(records)


def main():
    summary = process_dataset(SOURCE_DIR, JSON_OUTPUT, CSV_OUTPUT)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
