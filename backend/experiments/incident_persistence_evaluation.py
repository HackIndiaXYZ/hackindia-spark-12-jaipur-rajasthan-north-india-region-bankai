import os
import sys
from datetime import datetime

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.simulator import SensorSimulator, SimulationConfig
from app.services.incident_service import IncidentService
from app.db.database import SessionLocal, init_db
from app.db.repositories.incident_repository import IncidentRepository


def run_persistence_evaluation():
    init_db()
    db = SessionLocal()
    try:
        simulator = SensorSimulator()
        service = IncidentService()

        # 1. Generate gradual leak telemetry
        readings = simulator.generate_readings(SimulationConfig(
            scenario_type="gradual_leak",
            affected_zone_id="Zone_B",
            affected_segment_id="B2-B3",
            leak_start_minute=15,
            seed=42
        ))

        print("=========================================================================")
        print("    AQUASENTINEL INCIDENT PERSISTENCE & LIFECYCLE EVALUATION REPORT      ")
        print("=========================================================================\n")

        # 2. Process and persist telemetry (First run)
        inc1 = service.process_and_persist_telemetry(readings, db=db)
        print(f"[STEP 1] Incident Analyzed & Persisted:")
        print(f"         ID:          {inc1.incident_id}")
        print(f"         Fingerprint: {inc1.fingerprint}")
        print(f"         Status:      {inc1.status.value}")
        print(f"         Segment:     {inc1.affected_segment}\n")

        # 3. Retrieve incident from DB by ID
        fetched = IncidentRepository.get_by_id(db, inc1.incident_id)
        print(f"[STEP 2] Retrieved Incident from DB by ID ({inc1.incident_id}):")
        print(f"         Status in DB: {fetched.status}")
        print(f"         Confidence:   {fetched.confidence:.3f}")
        print(f"         Flow Loss:    {fetched.estimated_flow_loss_lpm:.2f} LPM\n")

        # 4. Update status: OPEN -> ACKNOWLEDGED
        updated_ack = IncidentRepository.update_status(db, inc1.incident_id, "ACKNOWLEDGED")
        print(f"[STEP 3] Transition Status OPEN -> ACKNOWLEDGED:")
        print(f"         Updated Status: {updated_ack.status}\n")

        # 5. Update status: ACKNOWLEDGED -> RESOLVED
        updated_res = IncidentRepository.update_status(db, inc1.incident_id, "RESOLVED")
        print(f"[STEP 4] Transition Status ACKNOWLEDGED -> RESOLVED:")
        print(f"         Updated Status: {updated_res.status}\n")

        # 6. Re-analyze identical telemetry batch (Idempotency test)
        inc2 = service.process_and_persist_telemetry(readings, db=db)
        print(f"[STEP 5] Re-analyzed Identical Telemetry Batch (Deduplication Check):")
        print(f"         Returned ID:          {inc2.incident_id}")
        print(f"         Returned Fingerprint: {inc2.fingerprint}")
        print(f"         Returned Status:      {inc2.status.value}")

        is_deduplicated = (inc1.incident_id == inc2.incident_id) and (inc1.fingerprint == inc2.fingerprint)
        print(f"\n[DEDUPLICATION VERIFICATION]: {'SUCCESS (No duplicate created)' if is_deduplicated else 'FAILED'}")
        print("=========================================================================\n")

    finally:
        db.close()


if __name__ == "__main__":
    run_persistence_evaluation()
