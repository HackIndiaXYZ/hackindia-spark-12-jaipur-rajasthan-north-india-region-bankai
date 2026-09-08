import pytest
import numpy as np

from app.models.network import WaterNetwork, Sensor
from app.models.observability import BlindSpotLevel
from app.services.observability import ObservabilityService


def test_observability_scoring_and_normalization():
    service = ObservabilityService()
    
    # Detected, fast response (15 min delay), 3 responsive sensors out of 3 total, max score 0.90
    score = service.calculate_segment_score(
        detected=True,
        detection_delay_minutes=15.0,
        responsive_sensor_count=3,
        total_zone_sensors=3,
        maximum_anomaly_score=0.90
    )
    assert 0.70 <= score <= 1.00

    # Not detected -> score must be 0.0
    undetected_score = service.calculate_segment_score(
        detected=False,
        detection_delay_minutes=-1.0,
        responsive_sensor_count=0,
        total_zone_sensors=3,
        maximum_anomaly_score=0.20
    )
    assert undetected_score == 0.0


def test_blind_spot_classification():
    service = ObservabilityService()
    assert service.classify_blind_spot(0.85, True) == BlindSpotLevel.HIGH_OBSERVABILITY
    assert service.classify_blind_spot(0.65, True) == BlindSpotLevel.MEDIUM_OBSERVABILITY
    assert service.classify_blind_spot(0.45, True) == BlindSpotLevel.LOW_OBSERVABILITY
    assert service.classify_blind_spot(0.25, True) == BlindSpotLevel.CRITICAL_BLIND_SPOT
    assert service.classify_blind_spot(0.90, False) == BlindSpotLevel.CRITICAL_BLIND_SPOT


def test_network_observability_summary_aggregation():
    service = ObservabilityService()
    summary = service.analyze_network_observability(use_cache=False)

    assert summary.total_segments == 10
    assert 0.0 <= summary.overall_observability <= 1.0
    assert summary.high_observability_segments + summary.medium_observability_segments + summary.low_observability_segments + summary.blind_spots == 10
    assert summary.weakest_segment != ""
    assert summary.strongest_segment != ""


def test_candidate_location_generation():
    service = ObservabilityService()
    candidates = service.generate_candidate_locations()

    assert len(candidates) > 0
    # Check candidates are valid network node locations and not reservoir
    for cand_node, seg_id, z_id in candidates:
        assert cand_node in service.network.nodes
        assert "Reservoir" not in cand_node


def test_virtual_sensor_evaluation_and_ranking():
    service = ObservabilityService()
    ranked_candidates = service.evaluate_virtual_sensor_candidates()

    assert len(ranked_candidates) > 0
    
    # Ensure ranked in descending order by value_score
    for i in range(len(ranked_candidates) - 1):
        assert ranked_candidates[i].value_score >= ranked_candidates[i+1].value_score

    top = ranked_candidates[0]
    assert top.value_score > 0.0
    assert len(top.reasoning) > 0


def test_caching_behavior():
    service = ObservabilityService()
    
    # First call - populates cache
    summary1 = service.analyze_network_observability(use_cache=True)
    assert len(service._cache) == 1
    
    # Second call - retrieves from cache instantly
    summary2 = service.analyze_network_observability(use_cache=True)
    assert summary1 == summary2


def test_observability_spatial_regression():
    service = ObservabilityService()
    summary = service.analyze_network_observability(use_cache=False)
    seg_map = {s.segment_id: s for s in summary.segment_details}

    # Trunk segment B2-B3 vs Endpoint segment C2-C3
    b2_b3 = seg_map.get("B2-B3")
    c2_c3 = seg_map.get("C2-C3")

    assert b2_b3 is not None and c2_c3 is not None
    # Central industrial trunk B2-B3 has more sensor redundancy than C2-C3
    assert b2_b3.responsive_sensor_count >= c2_c3.responsive_sensor_count
