from fastapi import APIRouter, HTTPException
from typing import List, Optional

from app.schemas.reading import SensorReadingSchema
from app.schemas.incident import IncidentResultSchema
from app.models.reading import SensorReading
from app.services.incident_service import IncidentService

router = APIRouter(prefix="/incidents", tags=["Incidents"])
_incident_service = IncidentService()


@router.post("/analyze", response_model=Optional[IncidentResultSchema])
def analyze_telemetry(readings_in: List[SensorReadingSchema]):
    """
    Executes the end-to-end AquaSentinel incident detection, localization, and loss estimation pipeline
    on a list of sensor readings.
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

    result = _incident_service.process_telemetry(domain_readings)
    if not result:
        return None

    return IncidentResultSchema(**result.to_dict())
