from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.data_source import (
    DataSourceResponse,
    DataSourceListResponse,
    DataSourceSummaryResponse,
    ObservationResponse,
    ObservationListResponse
)
from app.services.government_data_service import GovernmentDataContextService

router = APIRouter(prefix="/data-sources", tags=["Government Data Context"])

# Instantiate service instance
_service = GovernmentDataContextService()


@router.get("", response_model=DataSourceListResponse)
def list_data_sources():
    """
    List available Rajasthan surface water government contextual datasets.
    Provides offline dataset metadata, provenance, and geographic scope.
    """
    sources = _service.list_sources()
    responses = [
        DataSourceResponse(
            source_id=s.source_id,
            dataset_name=s.dataset_name,
            agency=s.agency,
            source_organization=s.source_organization,
            geography=s.geography,
            data_frequency=s.data_frequency,
            start_date=s.start_date,
            end_date=s.end_date,
            format=s.format,
            local_file=s.local_file,
            source_type=s.source_type.value,
            description=s.description,
            unit=s.unit,
            zone=s.zone
        )
        for s in sources
    ]
    return DataSourceListResponse(sources=responses, total_count=len(responses))


@router.get("/{source_id}", response_model=DataSourceResponse)
def get_data_source(source_id: str):
    """
    Get metadata for a specific government dataset by source ID.
    """
    s = _service.get_source(source_id)
    if not s:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Data source '{source_id}' not found."
        )
    return DataSourceResponse(
        source_id=s.source_id,
        dataset_name=s.dataset_name,
        agency=s.agency,
        source_organization=s.source_organization,
        geography=s.geography,
        data_frequency=s.data_frequency,
        start_date=s.start_date,
        end_date=s.end_date,
        format=s.format,
        local_file=s.local_file,
        source_type=s.source_type.value,
        description=s.description,
        unit=s.unit,
        zone=s.zone
    )


@router.get("/{source_id}/summary", response_model=DataSourceSummaryResponse)
def get_data_source_summary(source_id: str):
    """
    Get statistical summary, coverage dates, and calibration statistics for a government data source.
    """
    summary = _service.get_summary(source_id)
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Data source '{source_id}' not found."
        )
    return DataSourceSummaryResponse(
        source_id=summary.source_id,
        latest_timestamp=summary.latest_timestamp,
        latest_value=summary.latest_value,
        unit=summary.unit,
        min_value=summary.min_value,
        max_value=summary.max_value,
        mean_value=summary.mean_value,
        median_value=summary.median_value,
        observation_count=summary.observation_count,
        missing_value_count=summary.missing_value_count,
        coverage_start=summary.coverage_start,
        coverage_end=summary.coverage_end,
        historical_mean_deviation=summary.historical_mean_deviation
    )


@router.get("/{source_id}/recent", response_model=ObservationListResponse)
def get_recent_observations(
    source_id: str,
    limit: int = Query(50, ge=1, le=500, description="Maximum recent observations to return")
):
    """
    Get recent contextual observations for a data source, bounded by limit.
    """
    source = _service.get_source(source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Data source '{source_id}' not found."
        )
    observations = _service.get_recent_context(source_id, limit=limit)
    obs_responses = [
        ObservationResponse(
            timestamp=o.timestamp,
            value=o.value,
            unit=o.unit,
            station_name=o.station_name,
            metadata=o.metadata
        )
        for o in observations
    ]
    return ObservationListResponse(
        source_id=source_id,
        observations=obs_responses,
        total_returned=len(obs_responses)
    )
