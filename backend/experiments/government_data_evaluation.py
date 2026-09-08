import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parents[1]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.services.government_data_service import GovernmentDataContextService


def run_evaluation():
    print("=========================================================================")
    print("        AQUASENTINEL GOVERNMENT DATA CONTEXT EVALUATION REPORT          ")
    print("=========================================================================\n")

    service = GovernmentDataContextService()
    sources = service.list_sources()

    print(f"Total Government Context Data Sources Discovered: {len(sources)}\n")

    for s in sources:
        print(f"[DATASET] {s.dataset_name}")
        print(f"   Source ID:     {s.source_id}")
        print(f"   Agency:        {s.agency}")
        print(f"   Geography:     {s.geography}")
        print(f"   Local File:    {s.local_file}")
        print(f"   Source Type:   {s.source_type.value}")
        print(f"   Unit:          {s.unit}")
        print(f"   Zone Mapping:  {s.zone or 'None (Regional Context Only)'}")

        summary = service.get_summary(s.source_id)
        if summary:
            print("   --- Statistical Summary ---")
            print(f"   Coverage:        {summary.coverage_start} -> {summary.coverage_end}")
            print(f"   Total Obs Count: {summary.observation_count}")
            print(f"   Missing Count:   {summary.missing_value_count}")
            print(f"   Min Value:       {summary.min_value} {summary.unit}")
            print(f"   Max Value:       {summary.max_value} {summary.unit}")
            print(f"   Mean Value:      {summary.mean_value} {summary.unit}")
            print(f"   Median Value:    {summary.median_value} {summary.unit}")
            print(f"   Latest Obs:      {summary.latest_timestamp} | Value: {summary.latest_value} {summary.unit}")
            print(f"   Mean Deviation:  {summary.historical_mean_deviation} {summary.unit}")

        recent = service.get_recent_context(s.source_id, limit=3)
        print(f"   Recent Context Bounded (Limit 3): {len(recent)} items returned.")
        for idx, obs in enumerate(recent, 1):
            print(f"     [{idx}] {obs.timestamp} | Station: {obs.station_name} | {obs.value} {obs.unit}")

        print("-" * 73 + "\n")

    # Verification of Determinism
    print("[DETERMINISM VERIFICATION]")
    sum1 = service.get_summary("rajasthan_rainfall_telemetry")
    sum2 = service.get_summary("rajasthan_rainfall_telemetry")

    if sum1.observation_count == sum2.observation_count and sum1.mean_value == sum2.mean_value:
        print("   Status: PASSED (Repeated parsing produces identical deterministic statistics)")
    else:
        print("   Status: FAILED (Output is non-deterministic)")

    print("=========================================================================\n")


if __name__ == "__main__":
    run_evaluation()
