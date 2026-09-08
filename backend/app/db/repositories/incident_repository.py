import hashlib
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session

from app.db.models import IncidentModel
from app.models.incident import IncidentResult, IncidentStatus, ALLOWED_TRANSITIONS
from app.core.logging import logger


def generate_incident_fingerprint(affected_segment: str, incident_type: str, detected_at: datetime) -> str:
    """
    Generates a deterministic SHA-256 fingerprint from stable incident parameters.
    Prevents duplicate database creation when identical telemetry windows are re-analyzed.
    """
    raw_str = f"{affected_segment}:{incident_type}:{detected_at.strftime('%Y-%m-%dT%H:%M')}"
    return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()[:16]


class IncidentRepository:
    """
    Data Access Repository for Incident ORM Models.
    Handles creation, deduplication, retrieval, listing, and lifecycle status updates.
    """

    @staticmethod
    def create_or_get(db: Session, result: IncidentResult) -> Tuple[IncidentModel, bool]:
        """
        Persists an IncidentResult in DB. If fingerprint already exists, returns existing model (idempotent).
        Returns Tuple[IncidentModel, created_flag]
        """
        fingerprint = generate_incident_fingerprint(
            affected_segment=result.affected_segment,
            incident_type=result.incident_type.value if hasattr(result.incident_type, 'value') else str(result.incident_type),
            detected_at=result.detected_at
        )

        # Check existing fingerprint
        existing = db.query(IncidentModel).filter(IncidentModel.fingerprint == fingerprint).first()
        if existing:
            logger.info(f"Duplicate incident detected with fingerprint {fingerprint}. Returning existing ID {existing.incident_id}.")
            return existing, False

        # Create new model
        model = IncidentModel(
            incident_id=result.incident_id,
            fingerprint=fingerprint,
            incident_type=result.incident_type.value if hasattr(result.incident_type, 'value') else str(result.incident_type),
            severity=result.severity.value if hasattr(result.severity, 'value') else str(result.severity),
            status=result.status.value if hasattr(result.status, 'value') else str(result.status),
            affected_segment=result.affected_segment,
            affected_zone=result.affected_zone,
            detected_at=result.detected_at,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            detection_delay_min=result.detection_delay_min,
            confidence=result.confidence,
            observability_score=result.observability_score,
            estimated_flow_loss_lpm=result.estimated_flow_loss_lpm,
            estimated_volume_loss_liters=result.estimated_volume_loss_liters,
            evidence=result.evidence,
            responsive_sensors=result.responsive_sensors,
            candidate_segments=[c.to_dict() if hasattr(c, 'to_dict') else c for c in result.candidate_segments],
            disclaimer=result.disclaimer
        )

        db.add(model)
        db.commit()
        db.refresh(model)
        return model, True

    @staticmethod
    def get_by_id(db: Session, incident_id: str) -> Optional[IncidentModel]:
        return db.query(IncidentModel).filter(IncidentModel.incident_id == incident_id).first()

    @staticmethod
    def list_incidents(
        db: Session,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[IncidentModel]:
        query = db.query(IncidentModel)

        if status:
            query = query.filter(IncidentModel.status == status.upper())
        if severity:
            query = query.filter(IncidentModel.severity == severity.upper())

        return query.order_by(IncidentModel.detected_at.desc()).offset(offset).limit(limit).all()

    @staticmethod
    def update_status(db: Session, incident_id: str, new_status_str: str) -> IncidentModel:
        model = db.query(IncidentModel).filter(IncidentModel.incident_id == incident_id).first()
        if not model:
            raise KeyError(f"Incident with ID {incident_id} not found.")

        current_status = IncidentStatus(model.status)
        try:
            new_status = IncidentStatus(new_status_str.upper())
        except ValueError:
            raise ValueError(f"Unknown status '{new_status_str}'. Must be one of OPEN, ACKNOWLEDGED, RESOLVED.")

        # Validate allowed transitions
        if new_status != current_status:
            allowed = ALLOWED_TRANSITIONS.get(current_status, set())
            if new_status not in allowed:
                raise ValueError(f"Invalid status transition from '{current_status.value}' to '{new_status.value}'.")

            model.status = new_status.value
            model.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(model)

        return model
