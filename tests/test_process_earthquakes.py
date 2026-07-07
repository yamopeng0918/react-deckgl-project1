import csv
import json
import tempfile
import unittest
from pathlib import Path

from scripts.process_earthquakes import process_dataset


HEADERS = ["編號", "地震時間", "經度", "緯度", "規模", "深度", "最大震度", "位置"]


def write_source_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="cp950") as file:
        writer = csv.DictWriter(file, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(rows)


class ProcessEarthquakesTest(unittest.TestCase):
    def test_includes_update_subfolder_with_stable_source_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_dir = root / "source"
            json_output = root / "public" / "data" / "earthquakes.json"
            csv_output = root / "data" / "processed" / "earthquakes.csv"

            write_source_csv(
                source_dir / "update" / "earthquakes_202606.csv",
                [
                    {
                        HEADERS[0]: "update-001",
                        HEADERS[1]: "2026-06-30 05:15:02",
                        HEADERS[2]: "121.12",
                        HEADERS[3]: "23.45",
                        HEADERS[4]: "4.4",
                        HEADERS[5]: "18.2",
                        HEADERS[6]: "3",
                        HEADERS[7]: "Updated event",
                    }
                ],
            )

            summary = process_dataset(source_dir, json_output, csv_output)

            self.assertEqual(summary["source_files"], 1)
            self.assertEqual(summary["total_input_rows"], 1)
            self.assertEqual(summary["exported_rows"], 1)
            self.assertEqual(summary["included_years"], [2026])

            records = json.loads(json_output.read_text(encoding="utf-8"))
            self.assertEqual(records[0]["id"], "update-001")
            self.assertEqual(records[0]["year"], 2026)
            self.assertEqual(records[0]["source_file"], "update/earthquakes_202606.csv")

    def test_merges_yearly_and_2025_monthly_csvs_into_normalized_outputs(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_dir = root / "source"
            json_output = root / "public" / "data" / "earthquakes.json"
            csv_output = root / "data" / "processed" / "earthquakes.csv"

            write_source_csv(
                source_dir / "地震活動彙整_1995.csv",
                [
                    {
                        "編號": "071   ",
                        "地震時間": "1995-12-26 03:05:28",
                        "經度": "121.36",
                        "緯度": "22.82",
                        "規模": "4.9",
                        "深度": "12.5",
                        "最大震度": "4",
                        "位置": "台東市地震站東偏北方  22.8  公里",
                    }
                ],
            )
            write_source_csv(
                source_dir / "2025" / "地震活動彙整_202501.csv",
                [
                    {
                        "編號": "小區域有感地震",
                        "地震時間": "2025-01-31 23:19:09",
                        "經度": "121.684",
                        "緯度": "23.9102",
                        "規模": "4",
                        "深度": "52.1",
                        "最大震度": "1",
                        "位置": "花蓮縣政府東南方  11.1  公里",
                    }
                ],
            )

            summary = process_dataset(source_dir, json_output, csv_output)

            self.assertEqual(summary["total_input_rows"], 2)
            self.assertEqual(summary["exported_rows"], 2)
            self.assertEqual(summary["invalid_rows"], 0)
            self.assertEqual(summary["included_years"], [1995, 2025])

            records = json.loads(json_output.read_text(encoding="utf-8"))
            self.assertEqual(len(records), 2)
            self.assertEqual(
                set(records[0].keys()),
                {
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
                },
            )
            self.assertEqual(records[0]["id"], "071")
            self.assertEqual(records[0]["year"], 1995)
            self.assertEqual(records[0]["longitude"], 121.36)
            self.assertEqual(records[1]["id"], "小區域有感地震")
            self.assertEqual(records[1]["year"], 2025)

            with csv_output.open(newline="", encoding="utf-8") as file:
                csv_records = list(csv.DictReader(file))

            self.assertEqual(len(csv_records), 2)
            self.assertEqual(csv_records[0]["event_time"], "1995-12-26T03:05:28")

    def test_excludes_rows_with_invalid_required_values(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_dir = root / "source"
            json_output = root / "earthquakes.json"
            csv_output = root / "earthquakes.csv"

            write_source_csv(
                source_dir / "地震活動彙整_2024.csv",
                [
                    {
                        "編號": "514",
                        "地震時間": "2024-12-30 03:51:36",
                        "經度": "120.685",
                        "緯度": "23.5383",
                        "規模": "5.2",
                        "深度": "15.1",
                        "最大震度": "4",
                        "位置": "嘉義縣政府東北東方  40.9  公里",
                    },
                    {
                        "編號": "bad-lon",
                        "地震時間": "2024-12-30 10:04:39",
                        "經度": "999",
                        "緯度": "24.1803",
                        "規模": "3.5",
                        "深度": "26.8",
                        "最大震度": "1",
                        "位置": "無效經度",
                    },
                    {
                        "編號": "bad-mag",
                        "地震時間": "2024-12-29 23:22:12",
                        "經度": "121.545",
                        "緯度": "23.5323",
                        "規模": "",
                        "深度": "40",
                        "最大震度": "2",
                        "位置": "無效規模",
                    },
                ],
            )

            summary = process_dataset(source_dir, json_output, csv_output)

            self.assertEqual(summary["total_input_rows"], 3)
            self.assertEqual(summary["exported_rows"], 1)
            self.assertEqual(summary["invalid_rows"], 2)
            records = json.loads(json_output.read_text(encoding="utf-8"))
            self.assertEqual([record["id"] for record in records], ["514"])


if __name__ == "__main__":
    unittest.main()
