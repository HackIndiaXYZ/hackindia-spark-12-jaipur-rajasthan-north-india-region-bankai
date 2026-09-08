import os
import csv
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

from app.models.data_source import GovernmentDataSource, GovernmentObservation, SourceType
from app.core.logging import logger


class GovernmentDataLoader:
    """
    Offline-first safe CSV and JSON loader for NWDP / Rajasthan surface water datasets.
    Handles timestamp normalization, missing value safety, and deterministic record parsing.
    """

    def __init__(self, search_paths: Optional[List[Path]] = None):
        if search_paths is None:
            # Look in backend, project root, backend/data, etc.
            base_dir = Path(__file__).resolve().parents[3]  # Project Root
            backend_dir = Path(__file__).resolve().parents[2]  # backend/
            cwd = Path.cwd()
            self.search_paths = [base_dir, backend_dir, cwd, cwd / "data"]
        else:
            self.search_paths = search_paths

    def locate_file(self, filename: str) -> Optional[Path]:
        """Locates a dataset file safely across registered search paths."""
        for path in self.search_paths:
            candidate = path / filename
            if candidate.exists() and candidate.is_file():
                return candidate
        return None

    @staticmethod
    def parse_timestamp(ts_str: Optional[str]) -> Optional[str]:
        """
        Parses timestamps from various Rajasthan telemetry formats safely.
        Expected format: 'DD-MM-YYYY HH:MM' -> returns ISO string 'YYYY-MM-DD HH:MM'.
        """
        if not ts_str or not isinstance(ts_str, str):
            return None
        cleaned = ts_str.strip()
        if not cleaned or cleaned == "-":
            return None

        formats = [
            "%d-%m-%Y %H:%M",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%d/%m/%Y %H:%M",
            "%d-%m-%Y %H:%M:%S"
        ]

        for fmt in formats:
            try:
                dt = datetime.strptime(cleaned, fmt)
                return dt.strftime("%Y-%m-%d %H:%M")
            except ValueError:
                continue

        return cleaned

    @staticmethod
    def parse_numeric(val: Any) -> Optional[float]:
        """Safely parses float numeric values from raw strings or numbers."""
        if val is None:
            return None
        if isinstance(val, (int, float)):
            return float(val)
        if isinstance(val, str):
            cleaned = val.strip()
            if not cleaned or cleaned in ("-", "null", "None", "NaN", "N/A"):
                return None
            try:
                return float(cleaned)
            except ValueError:
                return None
        return None

    def load_rainfall_csv(self, filename: str) -> Tuple[List[GovernmentObservation], int]:
        """Loads and normalizes Rajasthan Rainfall Telemetry CSV file."""
        filepath = self.locate_file(filename)
        if not filepath:
            logger.warning(f"Rainfall CSV file not found: {filename}")
            return [], 0

        observations: List[GovernmentObservation] = []
        missing_count = 0

        try:
            with open(filepath, mode="r", encoding="utf-8", errors="replace") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    raw_ts = row.get("Data Acquisition Time")
                    norm_ts = self.parse_timestamp(raw_ts)
                    raw_val = row.get("Telemetry Hourly Rainfall (mm)")
                    val = self.parse_numeric(raw_val)

                    # Filter out sentinel error values (e.g. negative values or overflow 2147480100)
                    if val is not None and (val < 0 or val > 1000.0):
                        val = None

                    if norm_ts is None or val is None:
                        missing_count += 1
                        if norm_ts is None:
                            continue

                    obs_val = val if val is not None else 0.0
                    station = row.get("Station", "Unknown Station").strip()

                    observations.append(
                        GovernmentObservation(
                            timestamp=norm_ts,
                            value=obs_val,
                            unit="mm",
                            station_name=station,
                            metadata={
                                "district": row.get("District", "").strip(),
                                "basin": row.get("Basin", "").strip(),
                                "river": row.get("River", "").strip(),
                                "agency": row.get("Agency", "Rajasthan SW").strip()
                            }
                        )
                    )
        except Exception as e:
            logger.error(f"Error loading rainfall CSV {filename}: {e}")

        return observations, missing_count

    def load_discharge_json(self, filename: str) -> Tuple[List[GovernmentObservation], int]:
        """Loads and normalizes Rajasthan NWDP Canal/Dam Discharge JSON dataset."""
        filepath = self.locate_file(filename)
        if not filepath:
            logger.warning(f"Discharge JSON file not found: {filename}")
            return [], 0

        observations: List[GovernmentObservation] = []
        missing_count = 0

        try:
            with open(filepath, mode="r", encoding="utf-8", errors="replace") as f:
                data = json.load(f)

            records = data.get("result", {}).get("records", [])
            for rec in records:
                raw_ts = rec.get("Data Acquisition Time")
                norm_ts = self.parse_timestamp(raw_ts)
                if not norm_ts:
                    missing_count += 1
                    continue

                # Sum all gate discharge fields (e.g. "Gate-1 Discharge (cusec)")
                total_discharge = 0.0
                has_valid_gate = False

                for key, val in rec.items():
                    if "Discharge" in key:
                        parsed_val = self.parse_numeric(val)
                        if parsed_val is not None:
                            total_discharge += parsed_val
                            has_valid_gate = True

                if not has_valid_gate:
                    missing_count += 1

                station = rec.get("Station", "Discharge Station").strip()
                observations.append(
                    GovernmentObservation(
                        timestamp=norm_ts,
                        value=total_discharge,
                        unit="cusec",
                        station_name=station,
                        metadata={
                            "district": rec.get("District", "").strip(),
                            "agency": rec.get("Agency", "Rajasthan SW").strip(),
                            "latitude": rec.get("Latitude", "").strip(),
                            "longitude": rec.get("Longitude", "").strip()
                        }
                    )
                )
        except Exception as e:
            logger.error(f"Error loading discharge JSON {filename}: {e}")

        return observations, missing_count
