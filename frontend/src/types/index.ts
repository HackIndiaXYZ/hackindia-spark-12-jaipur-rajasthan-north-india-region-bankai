export type IncidentStatus = "OPEN" | "ACKNOWLEDGED" | "RESOLVED";
export type IncidentSeverity = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
export type IncidentType = "LEAK_SUSPECTED" | "BURST_SUSPECTED" | "SENSOR_FAULT" | "ANOMALY_UNCLASSIFIED";

export interface CandidateSegmentScore {
  segment_id: string;
  confidence: number;
  reason: string;
}

export interface Incident {
  incident_id: string;
  fingerprint: string;
  incident_type: IncidentType;
  severity: IncidentSeverity;
  status: IncidentStatus;
  affected_segment: string;
  affected_zone: string;
  detected_at: string;
  created_at: string;
  updated_at: string;
  detection_delay_min: number;
  confidence: number;
  responsive_sensors: string[];
  estimated_flow_loss_lpm: number;
  estimated_volume_loss_liters: number;
  candidate_segments: CandidateSegmentScore[];
  evidence: string[];
  observability_score: number;
  disclaimer: string;
}

export interface Zone {
  zone_id: string;
  name: string;
  description: string;
  target_pressure_bar: number;
  target_flow_lpm: number;
}

export interface NetworkNode {
  node_id: string;
  node_type: string; // RESERVOIR, JUNCTION, CONSUMER
  elevation_m: number;
  zone_id: string;
}

export interface PipelineSegment {
  segment_id: string;
  source_node: string;
  destination_node: string;
  zone_id: string;
  length_m: number;
  nominal_min_flow: number;
  nominal_max_flow: number;
  nominal_min_pressure: number;
  nominal_max_pressure: number;
}

export interface Sensor {
  sensor_id: string;
  zone_id: string;
  pipeline_segment_id: string;
  location_node: string;
  sensor_type: string;
  installation_metadata?: Record<string, unknown>;
  health_status: "HEALTHY" | "DEGRADED" | "FAULTY";
}

export interface NetworkTopology {
  name: string;
  zones: Zone[];
  nodes: NetworkNode[];
  segments: PipelineSegment[];
  sensors: Sensor[];
}

export interface NetworkStatus {
  network_status: "HEALTHY" | "DEGRADED" | "FAULTY";
  total_sensors: number;
  healthy_sensors: number;
  degraded_sensors: number;
  faulty_sensors: number;
  active_anomalies: number;
  active_leaks: number;
  estimated_total_loss_lpm: number;
}

export interface GovernmentDataSource {
  source_id: string;
  dataset_name: string;
  agency: string;
  source_organization: string;
  geography: string;
  data_frequency: string;
  start_date?: string;
  end_date?: string;
  format: string;
  local_file: string;
  source_type: string;
  description: string;
  unit: string;
  zone?: string | null;
}

export interface GovernmentObservationSummary {
  source_id: string;
  latest_timestamp?: string;
  latest_value?: number;
  unit: string;
  min_value?: number;
  max_value?: number;
  mean_value?: number;
  median_value?: number;
  observation_count: number;
  missing_value_count: number;
  coverage_start?: string;
  coverage_end?: string;
  historical_mean_deviation?: number;
}

export interface GovernmentObservation {
  timestamp: string;
  value: number;
  unit: string;
  station_name: string;
  metadata?: Record<string, unknown>;
}

export interface SensorReading {
  timestamp: string;
  sensor_id: string;
  zone_id: string;
  pipeline_segment_id: string;
  pressure: number;
  flow_rate: number;
  temperature: number;
  sensor_health: "HEALTHY" | "DEGRADED" | "FAULTY";
}

export type ScenarioType = "normal" | "gradual_leak" | "sudden_burst" | "sensor_fault";
