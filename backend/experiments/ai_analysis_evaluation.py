import sys
import os
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parents[1]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.services.ai_service import AIAnalysisService


def run_evaluation():
    print("=========================================================================")
    print("       AQUASENTINEL GROUNDED AI ANALYSIS EVALUATION REPORT             ")
    print("=========================================================================\n")

    ai_service = AIAnalysisService()

    test_incidents = [
        {
            "incident_id": "INC-GRADUAL-LEAK-EVAL",
            "incident_type": "LEAK_SUSPECTED",
            "severity": "CRITICAL",
            "affected_segment": "B2-B3",
            "affected_zone": "Zone_B",
            "confidence": 0.879,
            "observability_score": 0.897,
            "detection_delay_min": 15.0,
            "estimated_flow_loss_lpm": 30.94,
            "estimated_volume_loss_liters": 1082.8,
            "responsive_sensors": ["B1", "B2", "B3", "B4"],
            "candidate_segments": [{"segment_id": "B2-B3", "confidence": 0.91}],
            "evidence": ["Correlated pressure drop (-0.68 bar) detected across responsive sensors B2 and B3."]
        },
        {
            "incident_id": "INC-SENSOR-FAULT-EVAL",
            "incident_type": "SENSOR_FAULT",
            "severity": "HIGH",
            "affected_segment": "B2-B3",
            "affected_zone": "Zone_B",
            "confidence": 0.912,
            "observability_score": 0.85,
            "detection_delay_min": 1.0,
            "estimated_flow_loss_lpm": 0.0,
            "estimated_volume_loss_liters": 0.0,
            "responsive_sensors": ["B3"],
            "candidate_segments": [],
            "evidence": ["Sensor B3 spike fault (+2.8 bar). Neighboring sensors B2 & B4 remain normal."]
        },
        {
            "incident_id": "INC-BURST-EVENT-EVAL",
            "incident_type": "BURST_SUSPECTED",
            "severity": "CRITICAL",
            "affected_segment": "B2-B3",
            "affected_zone": "Zone_B",
            "confidence": 0.965,
            "observability_score": 0.925,
            "detection_delay_min": 2.0,
            "estimated_flow_loss_lpm": 78.5,
            "estimated_volume_loss_liters": 2355.0,
            "responsive_sensors": ["B1", "B2", "B3", "B4"],
            "candidate_segments": [{"segment_id": "B2-B3", "confidence": 0.96}],
            "evidence": ["Catastrophic pressure transient (-1.45 bar in <2 min) recorded at B2 & B3."]
        }
    ]

    for idx, inc in enumerate(test_incidents, 1):
        print(f"[{idx}] Evaluating Scenario: {inc['incident_type']} (ID: {inc['incident_id']})")
        res = ai_service.analyze_incident(inc, force_refresh=True)

        print(f"    Provider Used:   {res.provider}")
        print(f"    Summary:         {res.analysis.summary}")
        print("    Why Detected:")
        for r in res.analysis.why_detected:
            print(f"      • {r}")
        print("    Recommended Actions:")
        for a in res.analysis.recommended_actions:
            print(f"      - {a}")
        print(f"    Confidence Note: {res.analysis.confidence_note}")
        print(f"    Limitations:     {res.analysis.limitations}")
        print("-" * 73 + "\n")

    # Grounding & Fallback Verification
    print("[GROUNDING & FALLBACK VERIFICATION]")

    # Temporarily remove client to force fallback verification
    original_client = ai_service._client
    ai_service._client = None
    fallback_res = ai_service.analyze_incident(test_incidents[0], force_refresh=True)
    ai_service._client = original_client

    if fallback_res.provider == "deterministic_fallback" and "B2-B3" in fallback_res.analysis.summary:
        print("   Fallback Mode: PASSED (Returns grounded deterministic facts when API is offline)")
    else:
        print("   Fallback Mode: FAILED")

    print("=========================================================================\n")


if __name__ == "__main__":
    run_evaluation()
