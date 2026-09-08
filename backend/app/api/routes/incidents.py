from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.schemas.reading import SensorReadingSchema
from app.schemas.incident import IncidentResultSchema, IncidentStatusUpdateSchema
from app.schemas.ai_analysis import AIAnalysisResponse
from app.models.reading import SensorReading
from app.models.incident import IncidentResult, CandidateSegmentScore
from app.services.incident_service import IncidentService
from app.db.repositories.incident_repository import IncidentRepository
from app.db.database import get_db

router = APIRouter(prefix="/incidents", tags=["Incidents"])
_incident_service = IncidentService()


def _model_to_schema(model) -> IncidentResultSchema:
    cand_segments = []
    if model.candidate_segments:
        for c in model.candidate_segments:
            if isinstance(c, dict):
                cand_segments.append(c)
            elif hasattr(c, "to_dict"):
                cand_segments.append(c.to_dict())

    return IncidentResultSchema(
        incident_id=model.incident_id,
        fingerprint=model.fingerprint,
        incident_type=model.incident_type,
        severity=model.severity,
        status=model.status,
        affected_segment=model.affected_segment,
        affected_zone=model.affected_zone,
        detected_at=model.detected_at,
        created_at=model.created_at,
        updated_at=model.updated_at,
        detection_delay_min=model.detection_delay_min,
        confidence=model.confidence,
        responsive_sensors=model.responsive_sensors or [],
        estimated_flow_loss_lpm=model.estimated_flow_loss_lpm,
        estimated_volume_loss_liters=model.estimated_volume_loss_liters,
        candidate_segments=cand_segments,
        evidence=model.evidence or [],
        observability_score=model.observability_score,
        disclaimer=model.disclaimer or "Loss values are model-derived simulation estimates intended for demonstration and system evaluation."
    )


@router.post("/analyze", response_model=Optional[IncidentResultSchema])
def analyze_telemetry(readings_in: List[SensorReadingSchema], db: Session = Depends(get_db)):
    """
    Executes the end-to-end AquaSentinel incident detection, localization, and loss estimation pipeline
    on a list of sensor readings and persists the result idempotently.
    """
    if not readings_in:
        raise HTTPException(status_code=400, detail="Readings list cannot be empty.")

    domain_readings = [
        SensorReading(
            timestamp=r.timestamp,
            sensor_id=r.sensor_id,
            zone_id=r.zone_id,
            pipeline_segment_id=r.pipeline_segment_id,
            pressure=r.pressure,
            flow_rate=r.flow_rate,
            temperature=r.temperature,
            sensor_health=r.sensor_health
        )
        for r in readings_in
    ]

    result = _incident_service.process_and_persist_telemetry(domain_readings, db=db)
    if not result:
        return None

    # Fetch persisted model
    model = IncidentRepository.get_by_id(db, result.incident_id)
    if model:
        return _model_to_schema(model)

    return IncidentResultSchema(**result.to_dict())


@router.get("", response_model=List[IncidentResultSchema])
def list_incidents(
    status: Optional[str] = Query(None, description="Filter by status (OPEN, ACKNOWLEDGED, RESOLVED)"),
    severity: Optional[str] = Query(None, description="Filter by severity (LOW, MEDIUM, HIGH, CRITICAL)"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Lists persisted pipeline incidents with optional status/severity filtering and pagination.
    """
    models = IncidentRepository.list_incidents(db=db, status=status, severity=severity, limit=limit, offset=offset)
    return [_model_to_schema(m) for m in models]


@router.get("/{incident_id}", response_model=IncidentResultSchema)
def get_incident_by_id(incident_id: str, db: Session = Depends(get_db)):
    """
    Retrieves a single persisted incident by its unique ID.
    """
    model = IncidentRepository.get_by_id(db=db, incident_id=incident_id)
    if not model:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")
    return _model_to_schema(model)


@router.patch("/{incident_id}/status", response_model=IncidentResultSchema)
def update_incident_status(
    incident_id: str,
    update_in: IncidentStatusUpdateSchema,
    db: Session = Depends(get_db)
):
    """
    Updates the lifecycle status of an existing incident (OPEN -> ACKNOWLEDGED -> RESOLVED).
    Rejects invalid status transitions with HTTP 400.
    """
    try:
        updated_model = IncidentRepository.update_status(db=db, incident_id=incident_id, new_status_str=update_in.status)
        return _model_to_schema(updated_model)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{incident_id}/ai-analysis", response_model=AIAnalysisResponse)
def get_ai_analysis_for_incident(
    incident_id: str,
    force_refresh: bool = Query(False, description="Force refresh AI analysis bypassing cache"),
    db: Session = Depends(get_db)
):
    """
    Generates or retrieves server-side grounded AI explainability analysis for a persisted incident.
    Returns structured analysis matching AIAnalysisResponse schema.
    """
    from app.services.ai_service import AIAnalysisService
    ai_service = AIAnalysisService()

    model = IncidentRepository.get_by_id(db=db, incident_id=incident_id)
    if not model:
        # If model not found in DB, check if demo/synthetic incident ID or raise 404
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")

    incident_dict = _model_to_schema(model).model_dump()
    return ai_service.analyze_incident(incident_dict, force_refresh=force_refresh)

