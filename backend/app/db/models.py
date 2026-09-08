from datetime import datetime
from sqlalchemy import (
    Column, String, Float, Integer, DateTime, ForeignKey, Text, JSON, Enum
)
from sqlalchemy.orm import relationship
import enum

from app.db.database import Base


class HealthStatusEnum(str, enum.Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    FAULTY = "FAULTY"


class IncidentStatusEnum(str, enum.Enum):
    DETECTED = "DETECTED"
    INVESTIGATING = "INVESTIGATING"
    CONFIRMED = "CONFIRMED"
    RESOLVED = "RESOLVED"


class ZoneModel(Base):
    __tablename__ = "zones"

    zone_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    target_pressure_bar = Column(Float, default=4.0)
    target_flow_lpm = Column(Float, default=100.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    pipeline_segments = relationship("PipelineSegmentModel", back_populates="zone", cascade="all, delete-orphan")
    sensors = relationship("SensorModel", back_populates="zone", cascade="all, delete-orphan")


class PipelineSegmentModel(Base):
    __tablename__ = "pipeline_segments"

    segment_id = Column(String, primary_key=True, index=True)
    source_node = Column(String, nullable=False)
    destination_node = Column(String, nullable=False)
    zone_id = Column(String, ForeignKey("zones.zone_id"), nullable=False)
    length_m = Column(Float, nullable=False, default=100.0)
    nominal_min_flow = Column(Float, nullable=False, default=50.0)
    nominal_max_flow = Column(Float, nullable=False, default=150.0)
    nominal_min_pressure = Column(Float, nullable=False, default=3.0)
    nominal_max_pressure = Column(Float, nullable=False, default=5.0)

    zone = relationship("ZoneModel", back_populates="pipeline_segments")
    sensors = relationship("SensorModel", back_populates="pipeline_segment", cascade="all, delete-orphan")


class SensorModel(Base):
    __tablename__ = "sensors"

    sensor_id = Column(String, primary_key=True, index=True)
    zone_id = Column(String, ForeignKey("zones.zone_id"), nullable=False)
    pipeline_segment_id = Column(String, ForeignKey("pipeline_segments.segment_id"), nullable=True)
    location_node = Column(String, nullable=False)
    sensor_type = Column(String, nullable=False, default="multi-sensor")  # pressure, flow, multi-sensor
    installation_date = Column(String, nullable=True)
    model = Column(String, nullable=True)
    firmware_version = Column(String, nullable=True)
    health_status = Column(String, default="HEALTHY")

    zone = relationship("ZoneModel", back_populates="sensors")
    pipeline_segment = relationship("PipelineSegmentModel", back_populates="sensors")
    readings = relationship("SensorReadingModel", back_populates="sensor", cascade="all, delete-orphan")


class SensorReadingModel(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    sensor_id = Column(String, ForeignKey("sensors.sensor_id"), nullable=False, index=True)
    zone_id = Column(String, nullable=False)
    pipeline_segment_id = Column(String, nullable=True)
    pressure = Column(Float, nullable=False)
    flow_rate = Column(Float, nullable=False)
    temperature = Column(Float, nullable=False, default=20.0)
    sensor_health = Column(String, default="HEALTHY")

    sensor = relationship("SensorModel", back_populates="readings")


class AnomalyModel(Base):
    __tablename__ = "anomalies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    sensor_id = Column(String, ForeignKey("sensors.sensor_id"), nullable=False)
    anomaly_score = Column(Float, nullable=False)
    signals = Column(JSON, nullable=False)  # List of signal descriptions
    is_active = Column(Integer, default=1)  # 1 for active, 0 for resolved


class LeakEventModel(Base):
    __tablename__ = "leak_events"

    incident_id = Column(String, primary_key=True, index=True)
    detected_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    zone_id = Column(String, nullable=False)
    segment_id = Column(String, nullable=False)
    severity = Column(String, nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    leak_probability = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    estimated_loss_lpm = Column(Float, nullable=False)
    status = Column(String, default="DETECTED")  # DETECTED, INVESTIGATING, CONFIRMED, RESOLVED
    candidate_segments = Column(JSON, nullable=True)
    evidence = Column(JSON, nullable=True)


class GovernmentDatasetModel(Base):
    __tablename__ = "government_datasets"

    id = Column(String, primary_key=True, index=True)
    source_name = Column(String, nullable=False)  # NWIC, Data.gov.in, ISRO/Bhuvan
    dataset_name = Column(String, nullable=False)
    retrieved_at = Column(DateTime, default=datetime.utcnow)
    raw_data = Column(JSON, nullable=True)
    normalized_data = Column(JSON, nullable=True)
    provenance_url = Column(String, nullable=True)
    is_cached = Column(Integer, default=1)


class AIAnalysisModel(Base):
    __tablename__ = "ai_analyses"

    analysis_id = Column(String, primary_key=True, index=True)
    incident_id = Column(String, ForeignKey("leak_events.incident_id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    summary = Column(Text, nullable=False)
    explanation = Column(Text, nullable=False)
    recommended_action = Column(Text, nullable=False)
    risk_assessment = Column(Text, nullable=False)
    uncertainty_notes = Column(Text, nullable=False)
    provider_used = Column(String, nullable=False)
