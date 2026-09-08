import { NetworkTopology, NetworkStatus, Incident, ScenarioType, SensorReading } from "@/types";

export const CANONICAL_TOPOLOGY: NetworkTopology = {
  name: "AquaSentinel Canonical Water Network",
  zones: [
    {
      zone_id: "Zone_A",
      name: "North Commercial Zone A",
      description: "Primary commercial and institutional district.",
      target_pressure_bar: 3.5,
      target_flow_lpm: 250.0
    },
    {
      zone_id: "Zone_B",
      name: "Central Residential Zone B",
      description: "High-density residential urban core.",
      target_pressure_bar: 3.0,
      target_flow_lpm: 320.0
    },
    {
      zone_id: "Zone_C",
      name: "South Industrial Zone C",
      description: "Industrial park and manufacturing area.",
      target_pressure_bar: 4.0,
      target_flow_lpm: 400.0
    }
  ],
  nodes: [
    { node_id: "R0", node_type: "RESERVOIR", elevation_m: 120.0, zone_id: "Zone_A" },
    { node_id: "A1", node_type: "JUNCTION", elevation_m: 105.0, zone_id: "Zone_A" },
    { node_id: "A2", node_type: "CONSUMER", elevation_m: 102.0, zone_id: "Zone_A" },
    { node_id: "A3", node_type: "CONSUMER", elevation_m: 100.0, zone_id: "Zone_A" },
    { node_id: "B1", node_type: "JUNCTION", elevation_m: 108.0, zone_id: "Zone_B" },
    { node_id: "B2", node_type: "JUNCTION", elevation_m: 104.0, zone_id: "Zone_B" },
    { node_id: "B3", node_type: "JUNCTION", elevation_m: 101.0, zone_id: "Zone_B" },
    { node_id: "B4", node_type: "CONSUMER", elevation_m: 98.0, zone_id: "Zone_B" },
    { node_id: "C1", node_type: "JUNCTION", elevation_m: 110.0, zone_id: "Zone_C" },
    { node_id: "C2", node_type: "CONSUMER", elevation_m: 106.0, zone_id: "Zone_C" },
    { node_id: "C3", node_type: "CONSUMER", elevation_m: 103.0, zone_id: "Zone_C" }
  ],
  segments: [
    { segment_id: "R-A1", source_node: "R0", destination_node: "A1", zone_id: "Zone_A", length_m: 1200, nominal_min_flow: 180, nominal_max_flow: 350, nominal_min_pressure: 3.2, nominal_max_pressure: 4.2 },
    { segment_id: "A1-A2", source_node: "A1", destination_node: "A2", zone_id: "Zone_A", length_m: 800, nominal_min_flow: 120, nominal_max_flow: 250, nominal_min_pressure: 3.0, nominal_max_pressure: 3.8 },
    { segment_id: "A2-A3", source_node: "A2", destination_node: "A3", zone_id: "Zone_A", length_m: 600, nominal_min_flow: 80, nominal_max_flow: 180, nominal_min_pressure: 2.8, nominal_max_pressure: 3.6 },
    { segment_id: "R-B1", source_node: "R0", destination_node: "B1", zone_id: "Zone_B", length_m: 1500, nominal_min_flow: 200, nominal_max_flow: 400, nominal_min_pressure: 3.0, nominal_max_pressure: 4.0 },
    { segment_id: "B1-B2", source_node: "B1", destination_node: "B2", zone_id: "Zone_B", length_m: 900, nominal_min_flow: 150, nominal_max_flow: 300, nominal_min_pressure: 2.8, nominal_max_pressure: 3.6 },
    { segment_id: "B2-B3", source_node: "B2", destination_node: "B3", zone_id: "Zone_B", length_m: 750, nominal_min_flow: 120, nominal_max_flow: 260, nominal_min_pressure: 2.6, nominal_max_pressure: 3.4 },
    { segment_id: "B3-B4", source_node: "B3", destination_node: "B4", zone_id: "Zone_B", length_m: 500, nominal_min_flow: 70, nominal_max_flow: 150, nominal_min_pressure: 2.4, nominal_max_pressure: 3.2 },
    { segment_id: "R-C1", source_node: "R0", destination_node: "C1", zone_id: "Zone_C", length_m: 1800, nominal_min_flow: 250, nominal_max_flow: 450, nominal_min_pressure: 3.5, nominal_max_pressure: 4.5 },
    { segment_id: "C1-C2", source_node: "C1", destination_node: "C2", zone_id: "Zone_C", length_m: 1100, nominal_min_flow: 180, nominal_max_flow: 320, nominal_min_pressure: 3.2, nominal_max_pressure: 4.0 },
    { segment_id: "C2-C3", source_node: "C2", destination_node: "C3", zone_id: "Zone_C", length_m: 850, nominal_min_flow: 100, nominal_max_flow: 220, nominal_min_pressure: 3.0, nominal_max_pressure: 3.8 }
  ],
  sensors: [
    { sensor_id: "A1", zone_id: "Zone_A", pipeline_segment_id: "R-A1", location_node: "A1", sensor_type: "PRESSURE_FLOW", health_status: "HEALTHY" },
    { sensor_id: "A2", zone_id: "Zone_A", pipeline_segment_id: "A1-A2", location_node: "A2", sensor_type: "PRESSURE_FLOW", health_status: "HEALTHY" },
    { sensor_id: "A3", zone_id: "Zone_A", pipeline_segment_id: "A2-A3", location_node: "A3", sensor_type: "PRESSURE_FLOW", health_status: "HEALTHY" },
    { sensor_id: "B1", zone_id: "Zone_B", pipeline_segment_id: "R-B1", location_node: "B1", sensor_type: "PRESSURE_FLOW", health_status: "HEALTHY" },
    { sensor_id: "B2", zone_id: "Zone_B", pipeline_segment_id: "B1-B2", location_node: "B2", sensor_type: "PRESSURE_FLOW", health_status: "HEALTHY" },
    { sensor_id: "B3", zone_id: "Zone_B", pipeline_segment_id: "B2-B3", location_node: "B3", sensor_type: "PRESSURE_FLOW", health_status: "HEALTHY" },
    { sensor_id: "B4", zone_id: "Zone_B", pipeline_segment_id: "B3-B4", location_node: "B4", sensor_type: "PRESSURE_FLOW", health_status: "HEALTHY" },
    { sensor_id: "C1", zone_id: "Zone_C", pipeline_segment_id: "R-C1", location_node: "C1", sensor_type: "PRESSURE_FLOW", health_status: "HEALTHY" },
    { sensor_id: "C2", zone_id: "Zone_C", pipeline_segment_id: "C1-C2", location_node: "C2", sensor_type: "PRESSURE_FLOW", health_status: "HEALTHY" },
    { sensor_id: "C3", zone_id: "Zone_C", pipeline_segment_id: "C2-C3", location_node: "C3", sensor_type: "PRESSURE_FLOW", health_status: "HEALTHY" }
  ]
};

export interface ScenarioDemoState {
  scenario: ScenarioType;
  networkStatus: NetworkStatus;
  incidents: Incident[];
  activeAnomalies: { sensor_id: string; type: string; severity: string }[];
  faultySensors: string[]; // e.g. ["B3"] for sensor_fault
  highlightedSegment: string | null; // e.g. "B2-B3" for leak
  aiAnalysis: {
    whyDetected: string[];
    recommendedActions: string[];
    confidenceNote: string;
    limitations: string;
  };
}

export const DEMO_INCIDENTS: Record<string, Incident> = {
  "INC-GRADUAL-LEAK": {
    incident_id: "INC-B2B3-LEAK",
    fingerprint: "6115773062af205d",
    incident_type: "LEAK_SUSPECTED",
    severity: "CRITICAL",
    status: "OPEN",
    affected_segment: "B2-B3",
    affected_zone: "Zone_B",
    detected_at: "2026-09-08T08:15:00Z",
    created_at: "2026-09-08T08:15:01Z",
    updated_at: "2026-09-08T08:15:01Z",
    detection_delay_min: 15.0,
    confidence: 0.879,
    responsive_sensors: ["B1", "B2", "B3", "B4"],
    estimated_flow_loss_lpm: 30.94,
    estimated_volume_loss_liters: 1082.8,
    candidate_segments: [
      { segment_id: "B2-B3", confidence: 0.91, reason: "Primary correlated pressure drop & flow variance between node B2 and B3" },
      { segment_id: "B1-B2", confidence: 0.42, reason: "Upstream segment exhibits secondary pressure drop" },
      { segment_id: "B3-B4", confidence: 0.38, reason: "Downstream segment experiencing reduced delivery pressure" }
    ],
    evidence: [
      "Correlated pressure drop (-0.68 bar) detected across responsive sensors B2 and B3.",
      "Net flow discrepancy of 30.94 LPM measured between B2 downstream flow and B3 intake.",
      "Topology agreement score: 0.897 across 4 adjacent monitoring nodes in Zone_B.",
      "Persistent anomalous trend sustained for 15 consecutive minutes."
    ],
    observability_score: 0.897,
    disclaimer: "Loss values are model-derived simulation estimates intended for demonstration and system evaluation."
  },
  "INC-BURST": {
    incident_id: "INC-ZONEB-BURST",
    fingerprint: "77289fa120c91e44",
    incident_type: "BURST_SUSPECTED",
    severity: "CRITICAL",
    status: "OPEN",
    affected_segment: "B2-B3",
    affected_zone: "Zone_B",
    detected_at: "2026-09-08T09:30:00Z",
    created_at: "2026-09-08T09:30:01Z",
    updated_at: "2026-09-08T09:30:01Z",
    detection_delay_min: 2.0,
    confidence: 0.965,
    responsive_sensors: ["B1", "B2", "B3", "B4"],
    estimated_flow_loss_lpm: 78.5,
    estimated_volume_loss_liters: 2355.0,
    candidate_segments: [
      { segment_id: "B2-B3", confidence: 0.96, reason: "Catastrophic pressure drop and high rate-of-change across segment B2-B3" }
    ],
    evidence: [
      "Sudden pressure transient (-1.45 bar in <2 min) recorded at B2 & B3.",
      "High rate-of-change flow surge (78.5 LPM loss rate).",
      "Correlated node agreement across full Zone_B downstream trunk."
    ],
    observability_score: 0.925,
    disclaimer: "Loss values are model-derived simulation estimates intended for demonstration and system evaluation."
  }
};

export const SCENARIO_STATES: Record<ScenarioType, ScenarioDemoState> = {
  normal: {
    scenario: "normal",
    networkStatus: {
      network_status: "HEALTHY",
      total_sensors: 10,
      healthy_sensors: 10,
      degraded_sensors: 0,
      faulty_sensors: 0,
      active_anomalies: 0,
      active_leaks: 0,
      estimated_total_loss_lpm: 0.0
    },
    incidents: [],
    activeAnomalies: [],
    faultySensors: [],
    highlightedSegment: null,
    aiAnalysis: {
      whyDetected: [
        "Network pressure and flow rates are within nominal operational bounds across all 10 sensors.",
        "Diurnal demand curves match baseline expectations for Zone A, Zone B, and Zone C.",
        "No graph neighbor disagreement or persistence anomalies detected."
      ],
      recommendedActions: [
        "Maintain routine monitoring schedule.",
        "Ensure regional government telemetry context remains updated."
      ],
      confidenceNote: "100% telemetry consistency across all 10 network sensors.",
      limitations: "Observability index reflects current sensor layout."
    }
  },
  gradual_leak: {
    scenario: "gradual_leak",
    networkStatus: {
      network_status: "DEGRADED",
      total_sensors: 10,
      healthy_sensors: 9,
      degraded_sensors: 1,
      faulty_sensors: 0,
      active_anomalies: 2,
      active_leaks: 1,
      estimated_total_loss_lpm: 30.94
    },
    incidents: [DEMO_INCIDENTS["INC-GRADUAL-LEAK"]],
    activeAnomalies: [
      { sensor_id: "B2", type: "PRESSURE_DROP", severity: "HIGH" },
      { sensor_id: "B3", type: "FLOW_DISCREPANCY", severity: "CRITICAL" }
    ],
    faultySensors: [],
    highlightedSegment: "B2-B3",
    aiAnalysis: {
      whyDetected: [
        "Sustained pressure drop (-0.68 bar) detected between sensor B2 and B3.",
        "Correlated flow rate variance (30.94 L/min) across adjacent network nodes.",
        "Topology agreement score: 0.897 across responsive sensors B1, B2, B3, B4 in Zone_B.",
        "Sustained anomaly persistence exceeding 15 minutes confirms physical network leak."
      ],
      recommendedActions: [
        "Dispatch field maintenance team to inspect pipeline segment B2-B3 in Zone B.",
        "Check downstream pressure at node B3 and isolate isolation valve V-B2 if flow loss escalates.",
        "Acknowledge incident in control console to record operator dispatch."
      ],
      confidenceNote: "87.9% confidence based on multi-signal correlation and topology graph agreement.",
      limitations: "Loss estimates (30.94 LPM) are model-derived simulation estimates."
    }
  },
  sudden_burst: {
    scenario: "sudden_burst",
    networkStatus: {
      network_status: "FAULTY",
      total_sensors: 10,
      healthy_sensors: 8,
      degraded_sensors: 2,
      faulty_sensors: 0,
      active_anomalies: 4,
      active_leaks: 1,
      estimated_total_loss_lpm: 78.5
    },
    incidents: [DEMO_INCIDENTS["INC-BURST"]],
    activeAnomalies: [
      { sensor_id: "B1", type: "PRESSURE_DROP", severity: "HIGH" },
      { sensor_id: "B2", type: "PRESSURE_DROP", severity: "CRITICAL" },
      { sensor_id: "B3", type: "FLOW_SURGE", severity: "CRITICAL" },
      { sensor_id: "B4", type: "PRESSURE_DROP", severity: "HIGH" }
    ],
    faultySensors: [],
    highlightedSegment: "B2-B3",
    aiAnalysis: {
      whyDetected: [
        "Catastrophic pressure drop (-1.45 bar in < 2 mins) recorded at sensor B2.",
        "High rate-of-change flow surge indicating structural pipe rupture on segment B2-B3.",
        "Correlated pressure collapse propagated to downstream node B4."
      ],
      recommendedActions: [
        "IMMEDIATE ACTION: Close isolation valves at node B2 and B3.",
        "Alert municipal emergency response for Zone B residential district.",
        "Reroute water supply via secondary feeder R-C1 if pressure drops below 2.0 bar."
      ],
      confidenceNote: "96.5% high-confidence burst classification.",
      limitations: "Burst loss estimate: 78.5 LPM (Model-derived)."
    }
  },
  sensor_fault: {
    scenario: "sensor_fault",
    networkStatus: {
      network_status: "DEGRADED",
      total_sensors: 10,
      healthy_sensors: 9,
      degraded_sensors: 0,
      faulty_sensors: 1,
      active_anomalies: 1,
      active_leaks: 0,
      estimated_total_loss_lpm: 0.0
    },
    incidents: [],
    activeAnomalies: [
      { sensor_id: "B3", type: "SENSOR_SPIKE_FAULT", severity: "HIGH" }
    ],
    faultySensors: ["B3"],
    highlightedSegment: null, // Pipeline segments B2-B3 and B3-B4 remain NORMAL!
    aiAnalysis: {
      whyDetected: [
        "Sensor B3 produced an erratic reading spike (pressure +2.8 bar, flow 0 LPM).",
        "Neighboring sensors B2 (upstream) and B4 (downstream) report completely normal pressures (3.0 bar).",
        "Zero spatial correlation or pressure propagation detected across pipeline network topology.",
        "CLASSIFICATION: SENSOR FAULT (False alarm prevented — pipeline is healthy)."
      ],
      recommendedActions: [
        "Do NOT declare a pipeline leak or dispatch pipe excavation team.",
        "Schedule field technician to inspect, recalibrate, or replace telemetry transducer B3.",
        "Flag sensor B3 as DEGRADED in monitoring dashboard."
      ],
      confidenceNote: "91.2% confidence that anomaly is isolated to sensor telemetry electronics.",
      limitations: "Zero estimated water loss."
    }
  }
};

export function generateScenarioReadings(scenario: ScenarioType): SensorReading[] {
  const baseTime = new Date().toISOString();

  return CANONICAL_TOPOLOGY.sensors.map((sensor) => {
    let pressure = 3.0;
    let flow = 200.0;
    let health: "HEALTHY" | "DEGRADED" | "FAULTY" = "HEALTHY";

    if (scenario === "gradual_leak") {
      if (sensor.sensor_id === "B2") {
        pressure = 2.45;
        flow = 240.0;
      } else if (sensor.sensor_id === "B3") {
        pressure = 2.30;
        flow = 209.06;
      }
    } else if (scenario === "sudden_burst") {
      if (sensor.sensor_id === "B2" || sensor.sensor_id === "B3") {
        pressure = 1.55;
        flow = 280.0;
      }
    } else if (scenario === "sensor_fault") {
      if (sensor.sensor_id === "B3") {
        pressure = 5.85; // Erratic spike
        flow = 0.0;
        health = "FAULTY";
      }
    }

    return {
      timestamp: baseTime,
      sensor_id: sensor.sensor_id,
      zone_id: sensor.zone_id,
      pipeline_segment_id: sensor.pipeline_segment_id,
      pressure,
      flow_rate: flow,
      temperature: 20.0,
      sensor_health: health
    };
  });
}
