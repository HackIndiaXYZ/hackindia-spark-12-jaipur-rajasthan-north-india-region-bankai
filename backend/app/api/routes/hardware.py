from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import time

from app.schemas.hardware import ESP32TelemetryPayload, HardwareStateResponse
from app.db.models import IncidentModel
from app.api.routes.incidents import _model_to_schema
from app.db.database import get_db
from app.core.config import settings
from app.core.logging import logger

router = APIRouter()

# In-memory store for hardware telemetry state
_latest_telemetry: Optional[ESP32TelemetryPayload] = None
_last_received_time: Optional[float] = None
_latest_incident_dict: Optional[Dict[str, Any]] = None
_latest_derived_flow: Optional[float] = None
_active_hardware_incident_id: Optional[str] = None


def verify_hardware_token(
    x_hardware_token: Optional[str] = Header(None, alias="X-Hardware-Token"),
    authorization: Optional[str] = Header(None)
):
    """
    Verify optional hardware ingest token if configured on the backend.
    """
    if not settings.HARDWARE_INGEST_TOKEN:
        return

    provided_token = x_hardware_token
    if not provided_token and authorization:
        if authorization.startswith("Bearer "):
            provided_token = authorization[7:].strip()
        else:
            provided_token = authorization.strip()

    if provided_token != settings.HARDWARE_INGEST_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid or missing hardware ingest token")


@router.post("/telemetry", response_model=HardwareStateResponse)
async def receive_hardware_telemetry(
    payload: ESP32TelemetryPayload,
    db: Session = Depends(get_db),
    _: None = Depends(verify_hardware_token)
):
    """
    Ingest ESP32 hardware telemetry from serial bridge (local or remote HTTPS).
    Maps FSR402 prototype sensor input (pressure_equivalent) into AquaSentinel pipeline.
    Creates or updates a persistent IncidentModel in SQLite DB while alert remains active.
    Resets active event tracking when sensor returns to NORMAL so future threshold crossings generate a NEW incident.
    """
    global _latest_telemetry, _last_received_time, _latest_incident_dict, _latest_derived_flow, _active_hardware_incident_id

    _latest_telemetry = payload
    _last_received_time = time.time()

    is_alert = payload.raw_value >= payload.threshold

    if is_alert:
        simulated_pressure = max(0.5, 4.2 - (payload.pressure_equivalent / 100.0) * 3.5)
        derived_flow = 120.0 + (payload.pressure_equivalent / 100.0) * 160.0
    else:
        simulated_pressure = 4.2
        derived_flow = 120.0

    _latest_derived_flow = derived_flow

    try:
        if is_alert:
            # Check if we have an ongoing active hardware incident in DB
            existing_model = None
            if _active_hardware_incident_id:
                existing_model = db.query(IncidentModel).filter(
                    IncidentModel.incident_id == _active_hardware_incident_id
                ).first()

            if existing_model and existing_model.status != "RESOLVED":
                # Continuous physical event: update peak force/pressure and loss metrics
                existing_model.peak_raw_adc = max(existing_model.peak_raw_adc or 0, payload.raw_value)
                existing_model.peak_pressure_equivalent = max(
                    existing_model.peak_pressure_equivalent or 0.0, payload.pressure_equivalent
                )
                existing_model.estimated_flow_loss_lpm = round(derived_flow - 120.0, 1)
                existing_model.updated_at = datetime.now(timezone.utc)
                db.commit()
                db.refresh(existing_model)

                inc_dict = _model_to_schema(existing_model).model_dump()
                inc_dict["disclaimer"] = (
                    "FSR402 prototype sensor input. Flow and volume loss values are model-derived simulation estimates for pipeline compatibility."
                )
                _latest_incident_dict = inc_dict
            else:
                # First threshold crossing or previous incident was resolved: create NEW persistent DB record
                inc_id = f"INC-HW-{payload.timestamp_ms}"
                fingerprint = f"HW-{payload.sensor_id}-{payload.timestamp_ms}"

                new_model = IncidentModel(
                    incident_id=inc_id,
                    fingerprint=fingerprint,
                    incident_type="BURST_EVENT",
                    severity="CRITICAL",
                    status="OPEN",
                    affected_segment=settings.ESP32_SEGMENT_ID,
                    affected_zone=settings.ESP32_ZONE_ID,
                    detected_at=datetime.now(timezone.utc),
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                    detection_delay_min=0.1,
                    confidence=0.92,
                    observability_score=0.91,
                    estimated_flow_loss_lpm=round(derived_flow - 120.0, 1),
                    estimated_volume_loss_liters=350.0,
                    evidence=[
                        f"Prototype FSR402 force input: raw ADC {payload.raw_value} (Pressure equivalent {payload.pressure_equivalent:.1f}%)",
                        "Significant correlated pressure drop detected on sensor B2 (Segment B2-B3).",
                        "Derived flow rate compatibility surge observed."
                    ],
                    responsive_sensors=["B2", "B3"],
                    candidate_segments=[
                        {"segment_id": "B2-B3", "confidence": 0.95, "reason": "FSR402 force input exceeding threshold"}
                    ],
                    peak_raw_adc=payload.raw_value,
                    peak_pressure_equivalent=payload.pressure_equivalent,
                    source="LIVE HARDWARE",
                    disclaimer="FSR402 prototype sensor input. Flow and volume loss values are model-derived simulation estimates for pipeline compatibility."
                )
                db.add(new_model)
                db.commit()
                db.refresh(new_model)

                _active_hardware_incident_id = inc_id

                inc_dict = _model_to_schema(new_model).model_dump()
                _latest_incident_dict = inc_dict
        else:
            # When FSR drops below threshold, reset active hardware incident ID so subsequent alert creates a NEW incident
            _active_hardware_incident_id = None
            _latest_incident_dict = None
    except Exception as e:
        logger.error(f"Error persisting hardware telemetry incident to DB: {e}")
        db.rollback()
        if is_alert:
            _latest_incident_dict = {
                "incident_id": f"INC-HW-{payload.timestamp_ms}",
                "incident_type": "BURST_EVENT",
                "severity": "CRITICAL",
                "status": "OPEN",
                "affected_segment": "B2-B3",
                "affected_zone": "Zone_B",
                "confidence": 0.92,
                "estimated_flow_loss_lpm": round(derived_flow - 120.0, 1),
                "estimated_volume_loss_liters": 350.0,
                "evidence": [
                    f"Prototype FSR402 force input: raw ADC {payload.raw_value} (Pressure equivalent {payload.pressure_equivalent:.1f}%)"
                ],
                "peak_raw_adc": payload.raw_value,
                "peak_pressure_equivalent": payload.pressure_equivalent,
                "source": "LIVE HARDWARE"
            }
        else:
            _latest_incident_dict = None

    return get_hardware_status_internal()


@router.get("/latest", response_model=HardwareStateResponse)
async def get_hardware_status():
    """
    Get latest ESP32 hardware connection state and telemetry.
    State is LIVE HARDWARE if telemetry was received within ESP32_STALE_THRESHOLD_SEC,
    DISCONNECTED if stale, or SIMULATION if no telemetry has been ingested.
    """
    return get_hardware_status_internal()


def get_hardware_status_internal() -> HardwareStateResponse:
    global _latest_telemetry, _last_received_time, _latest_incident_dict, _latest_derived_flow

    if _latest_telemetry is None or _last_received_time is None:
        return HardwareStateResponse(
            connection_state="SIMULATION",
            last_received_at=None,
            telemetry=None,
            derived_flow_lpm=None,
            pipeline_incident=None
        )

    elapsed_sec = time.time() - _last_received_time
    if elapsed_sec > settings.ESP32_STALE_THRESHOLD_SEC:
        connection_state = "DISCONNECTED"
        incident_dict = None
    else:
        connection_state = "LIVE HARDWARE"
        incident_dict = _latest_incident_dict

    iso_timestamp = datetime.fromtimestamp(_last_received_time, timezone.utc).isoformat()

    return HardwareStateResponse(
        connection_state=connection_state,
        last_received_at=iso_timestamp,
        telemetry=_latest_telemetry,
        derived_flow_lpm=_latest_derived_flow if connection_state == "LIVE HARDWARE" else None,
        pipeline_incident=incident_dict
    )

