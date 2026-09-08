import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from app.models.data_source import GovernmentDataSource, GovernmentObservationSummary, GovernmentObservation, SourceType
from app.services.government_data_loader import GovernmentDataLoader
from app.core.logging import logger


class GovernmentDataContextService:
    """
    Service for accessing offline government surface water data context & calibration statistics.
    Provides metadata, statistical summaries, and recent observations without live network calls.
    """

    def __init__(self, loader: Optional[GovernmentDataLoader] = None):
        self.loader = loader or GovernmentDataLoader()
        self._sources: Dict[str, GovernmentDataSource] = {}
        self._observations_cache: Dict[str, List[GovernmentObservation]] = {}
        self._summaries_cache: Dict[str, GovernmentObservationSummary] = {}
        self._initialize_sources()

    def _initialize_sources(self):
        """Registers the 3 official Rajasthan Surface Water NWDP datasets."""
        self._sources["rajasthan_rainfall_telemetry"] = GovernmentDataSource(
            source_id="rajasthan_rainfall_telemetry",
            dataset_name="Rajasthan Surface Water Telemetry Hourly Rainfall",
            agency="Rajasthan Surface Water Department",
            source_organization="National Water Data Portals / India WRIS",
            geography="Rajasthan, India",
            data_frequency="Hourly",
            start_date="2021-10-17 07:00",
            end_date="2030-01-01 08:00",
            format="CSV",
            local_file="rainfall_tel_hr_rajasthan_sw_rj_2021_2025.csv",
            source_type=SourceType.GOVERNMENT_TELEMETRY,
            description="Hourly regional rainfall telemetry observations from rain gauge stations in Rajasthan.",
            unit="mm",
            zone=None
        )

        self._sources["mahi_canal_discharge"] = GovernmentDataSource(
            source_id="mahi_canal_discharge",
            dataset_name="Mahi Head Regulator Canal Telemetry Hourly Discharge",
            agency="Rajasthan Surface Water Department",
            source_organization="National Water Data Portals / India WRIS",
            geography="Sikar / Banswara, Rajasthan, India",
            data_frequency="Hourly",
            start_date="2024-12-13 12:00",
            end_date="2026-03-25 15:00",
            format="JSON (NWDP Schema)",
            local_file="data (1).json",
            source_type=SourceType.GOVERNMENT_TELEMETRY,
            description="Hourly canal head regulator gate discharge telemetry measurements from Mahi Canal.",
            unit="cusec",
            zone=None
        )

        self._sources["bisalpur_dam_discharge"] = GovernmentDataSource(
            source_id="bisalpur_dam_discharge",
            dataset_name="Bisalpur Dam Reservoir Telemetry Hourly Discharge",
            agency="Rajasthan Surface Water Department",
            source_organization="National Water Data Portals / India WRIS",
            geography="Tonk, Rajasthan, India",
            data_frequency="Hourly",
            start_date="2024-03-06 04:00",
            end_date="2024-03-06 04:00",
            format="JSON (NWDP Schema)",
            local_file="data.json",
            source_type=SourceType.GOVERNMENT_TELEMETRY,
            description="Hourly dam spillway gate discharge telemetry measurements from Bisalpur Reservoir.",
            unit="cusec",
            zone=None
        )

    def _load_observations(self, source_id: str) -> Tuple[List[GovernmentObservation], int]:
        """Loads and caches raw observations for a given source ID."""
        if source_id in self._observations_cache:
            return self._observations_cache[source_id], 0

        source = self._sources.get(source_id)
        if not source:
            return [], 0

        if source_id == "rajasthan_rainfall_telemetry":
            obs1, miss1 = self.loader.load_rainfall_csv("rainfall_tel_hr_rajasthan_sw_rj_2021_2025.csv")
            obs2, miss2 = self.loader.load_rainfall_csv("rainfall_tel_hr_rajasthan_sw_rj_2026_2030.csv")
            all_obs = obs1 + obs2
            tot_miss = miss1 + miss2
        elif source_id == "mahi_canal_discharge":
            obs1, miss1 = self.loader.load_discharge_json("data (1).json")
            obs2, miss2 = self.loader.load_discharge_json("data (2).json")
            all_obs = obs1 + obs2
            tot_miss = miss1 + miss2
        elif source_id == "bisalpur_dam_discharge":
            all_obs, tot_miss = self.loader.load_discharge_json("data.json")
        else:
            all_obs, tot_miss = [], 0

        # Sort observations deterministically by timestamp
        all_obs.sort(key=lambda x: x.timestamp)
        self._observations_cache[source_id] = all_obs
        return all_obs, tot_miss

    def list_sources(self) -> List[GovernmentDataSource]:
        """Returns metadata for all registered government data sources."""
        return list(self._sources.values())

    def get_source(self, source_id: str) -> Optional[GovernmentDataSource]:
        """Returns metadata for a specific government data source."""
        return self._sources.get(source_id)

    def get_summary(self, source_id: str) -> Optional[GovernmentObservationSummary]:
        """Computes and returns summary statistics for a government data source."""
        if source_id in self._summaries_cache:
            return self._summaries_cache[source_id]

        source = self.get_source(source_id)
        if not source:
            return None

        observations, missing_count = self._load_observations(source_id)
        if not observations:
            summary = GovernmentObservationSummary(
                source_id=source_id,
                latest_timestamp=None,
                latest_value=None,
                unit=source.unit,
                min_value=None,
                max_value=None,
                mean_value=None,
                median_value=None,
                observation_count=0,
                missing_value_count=missing_count,
                coverage_start=None,
                coverage_end=None,
                historical_mean_deviation=None
            )
            self._summaries_cache[source_id] = summary
            return summary

        values = [obs.value for obs in observations]
        timestamps = [obs.timestamp for obs in observations]

        val_array = np.array(values, dtype=float)
        mean_val = float(np.mean(val_array))
        median_val = float(np.median(val_array))
        min_val = float(np.min(val_array))
        max_val = float(np.max(val_array))
        latest_obs = observations[-1]
        latest_val = latest_obs.value
        latest_ts = latest_obs.timestamp

        dev = latest_val - mean_val

        summary = GovernmentObservationSummary(
            source_id=source_id,
            latest_timestamp=latest_ts,
            latest_value=round(latest_val, 4),
            unit=source.unit,
            min_value=round(min_val, 4),
            max_value=round(max_val, 4),
            mean_value=round(mean_val, 4),
            median_value=round(median_val, 4),
            observation_count=len(observations),
            missing_value_count=missing_count,
            coverage_start=timestamps[0],
            coverage_end=timestamps[-1],
            historical_mean_deviation=round(dev, 4)
        )
        self._summaries_cache[source_id] = summary
        return summary

    def get_recent_context(self, source_id: str, limit: int = 50) -> List[GovernmentObservation]:
        """Returns the most recent observations for a source, bounded by limit."""
        observations, _ = self._load_observations(source_id)
        if not observations:
            return []
        safe_limit = max(1, min(limit, 500))
        return observations[-safe_limit:]
