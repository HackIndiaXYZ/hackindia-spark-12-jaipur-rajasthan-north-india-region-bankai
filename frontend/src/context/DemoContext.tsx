"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { ScenarioType, Incident } from "@/types";
import { SCENARIO_STATES, ScenarioDemoState, generateScenarioReadings } from "@/lib/demo/demoData";
import { checkBackendHealth, listIncidents, updateIncidentStatus, analyzeTelemetry, getApiEndpoint } from "@/lib/api/client";

interface HardwareTelemetryPayload {
  device_id: string;
  sensor_id: string;
  zone_id: string;
  raw_value: number;
  pressure_equivalent: number;
  threshold: number;
  status: string;
  timestamp_ms: number;
}

interface HardwareStateData {
  connection_state: "LIVE HARDWARE" | "DISCONNECTED" | "SIMULATION";
  last_received_at: string | null;
  telemetry: HardwareTelemetryPayload | null;
  derived_flow_lpm: number | null;
  pipeline_incident: Record<string, any> | null;
}

interface DemoContextType {
  scenario: ScenarioType;
  setScenario: (scenario: ScenarioType) => void;
  isBackendLive: boolean;
  isDemoMode: boolean;
  setIsDemoMode: (val: boolean) => void;
  isHardwareLive: boolean;
  hardwareState: HardwareStateData;
  activeState: ScenarioDemoState;
  incidents: Incident[];
  acknowledgeIncident: (id: string) => Promise<void>;
  resolveIncident: (id: string) => Promise<void>;
  refreshBackendData: () => Promise<void>;
}

const DemoContext = createContext<DemoContextType | undefined>(undefined);

export const DemoProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [scenario, setScenarioState] = useState<ScenarioType>("normal");
  const [isBackendLive, setIsBackendLive] = useState<boolean>(false);
  const [isDemoMode, setIsDemoMode] = useState<boolean>(false);
  const [demoState, setDemoState] = useState<ScenarioDemoState>(SCENARIO_STATES["normal"]);
  const [backendIncidents, setBackendIncidents] = useState<Incident[]>([]);

  // Hardware Live Telemetry State
  const [hardwareState, setHardwareState] = useState<HardwareStateData>({
    connection_state: "SIMULATION",
    last_received_at: null,
    telemetry: null,
    derived_flow_lpm: null,
    pipeline_incident: null,
  });

  // Check backend health periodically
  const checkHealth = useCallback(async () => {
    const live = await checkBackendHealth();
    setIsBackendLive(live);
  }, []);

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 10000);
    return () => clearInterval(interval);
  }, [checkHealth]);

  // Fetch backend persisted incidents
  const refreshBackendData = useCallback(async () => {
    if (isBackendLive) {
      try {
        const realIncidents = await listIncidents();
        setBackendIncidents(realIncidents);
      } catch (err) {
        console.warn("Error refreshing backend incidents:", err);
      }
    }
  }, [isBackendLive]);

  // Poll Hardware Telemetry Status & refresh persistent backend incident history
  useEffect(() => {
    const pollHardware = async () => {
      try {
        const res = await fetch(getApiEndpoint("/hardware/latest"), { cache: "no-store" });
        if (res.ok) {
          const data = await res.json();
          setHardwareState(data);
        }
      } catch (err) {
        setHardwareState((prev) => ({
          ...prev,
          connection_state: "DISCONNECTED",
        }));
      }
    };

    pollHardware();
    const hwInterval = setInterval(pollHardware, 500); // 500ms polling for live hardware reactivity
    return () => clearInterval(hwInterval);
  }, []);


  useEffect(() => {
    refreshBackendData();
    const histInterval = setInterval(refreshBackendData, 2000);
    return () => clearInterval(histInterval);
  }, [refreshBackendData]);

  // Handle scenario switching
  const setScenario = useCallback(async (newScenario: ScenarioType) => {
    setScenarioState(newScenario);
    const targetState = JSON.parse(JSON.stringify(SCENARIO_STATES[newScenario])) as ScenarioDemoState;
    setDemoState(targetState);

    if (isBackendLive && !isDemoMode) {
      try {
        const readings = generateScenarioReadings(newScenario);
        await analyzeTelemetry(readings);
        await refreshBackendData();
      } catch (err) {
        console.warn("Failed to submit telemetry to backend:", err);
      }
    }
  }, [isBackendLive, isDemoMode, refreshBackendData]);

  // Acknowledge incident handler
  const acknowledgeIncident = async (id: string) => {
    if (isBackendLive) {
      try {
        await updateIncidentStatus(id, "ACKNOWLEDGED");
        await refreshBackendData();
        return;
      } catch (err) {
        console.warn("Backend acknowledge update failed, updating local state:", err);
      }
    }

    setBackendIncidents((prev) =>
      prev.map((inc) =>
        inc.incident_id === id
          ? { ...inc, status: "ACKNOWLEDGED" as const, acknowledged_at: new Date().toISOString() }
          : inc
      )
    );

    setDemoState((prev) => {
      const updatedIncidents = prev.incidents.map((inc) =>
        inc.incident_id === id
          ? { ...inc, status: "ACKNOWLEDGED" as const, acknowledged_at: new Date().toISOString() }
          : inc
      );
      return { ...prev, incidents: updatedIncidents };
    });
  };

  // Resolve incident handler
  const resolveIncident = async (id: string) => {
    if (isBackendLive) {
      try {
        await updateIncidentStatus(id, "RESOLVED");
        await refreshBackendData();
        return;
      } catch (err) {
        console.warn("Backend resolve update failed, updating local state:", err);
      }
    }

    setBackendIncidents((prev) =>
      prev.map((inc) =>
        inc.incident_id === id
          ? { ...inc, status: "RESOLVED" as const, resolved_at: new Date().toISOString() }
          : inc
      )
    );

    setDemoState((prev) => {
      const updatedIncidents = prev.incidents.map((inc) =>
        inc.incident_id === id
          ? { ...inc, status: "RESOLVED" as const, resolved_at: new Date().toISOString() }
          : inc
      );

      return {
        ...prev,
        incidents: updatedIncidents,
        highlightedSegment: null,
        networkStatus: {
          ...prev.networkStatus,
          network_status: "HEALTHY",
          active_anomalies: 0,
          active_leaks: 0,
          estimated_total_loss_lpm: 0
        }
      };
    });
  };

  // Determine if hardware is actively driving the live state
  const isHardwareLive = hardwareState.connection_state === "LIVE HARDWARE";
  const isHardwareAlert = isHardwareLive && hardwareState.telemetry?.status === "ALERT";

  // Construct Live Hardware Incident from backend payload
  const liveHardwareIncident: Incident | null = isHardwareAlert
    ? {
        incident_id: hardwareState.pipeline_incident?.incident_id || "INC-ESP32-B2",
        fingerprint: hardwareState.pipeline_incident?.fingerprint || "FINGERPRINT-ESP32-B2",
        incident_type: "BURST_SUSPECTED",
        severity: "CRITICAL",
        status: (hardwareState.pipeline_incident?.status as any) || "OPEN",
        affected_segment: "B2-B3",
        affected_zone: "Zone_B",
        detected_at: hardwareState.pipeline_incident?.created_at || new Date().toISOString(),
        created_at: hardwareState.pipeline_incident?.created_at || new Date().toISOString(),
        updated_at: hardwareState.pipeline_incident?.updated_at || new Date().toISOString(),
        detection_delay_min: 0.1,
        confidence: hardwareState.pipeline_incident?.confidence || 0.92,
        responsive_sensors: ["B2", "B3"],
        estimated_flow_loss_lpm: Math.round(
          hardwareState.derived_flow_lpm ? Math.max(10, hardwareState.derived_flow_lpm - 120) : 104.0
        ),
        estimated_volume_loss_liters: 350,
        candidate_segments: [
          { segment_id: "B2-B3", confidence: 0.95, reason: "Correlated pressure drop on node B2 and derived flow surge" }
        ],
        evidence: hardwareState.pipeline_incident?.evidence || [
          `Prototype FSR402 force input: raw ADC ${hardwareState.telemetry?.raw_value} (Pressure equivalent ${hardwareState.telemetry?.pressure_equivalent.toFixed(1)}%)`,
          "Significant pressure drop detected on sensor B2 (Segment B2-B3).",
          "Derived flow rate compatibility surge observed."
        ],
        observability_score: 0.91,
        disclaimer: "FSR402 prototype sensor input. Flow and volume loss values are model-derived simulation estimates for pipeline compatibility."
      }
    : null;

  // Construct Effective Active Scenario State
  let effectiveState: ScenarioDemoState = demoState;

  if (isHardwareLive) {
    if (isHardwareAlert) {
      effectiveState = {
        scenario: "sudden_burst",
        networkStatus: {
          total_sensors: 10,
          healthy_sensors: 10,
          degraded_sensors: 0,
          faulty_sensors: 0,
          active_anomalies: 1,
          active_leaks: 1,
          estimated_total_loss_lpm: Math.round(
            hardwareState.derived_flow_lpm ? Math.max(10, hardwareState.derived_flow_lpm - 120) : 104.0
          ),
          network_status: "DEGRADED"
        },
        highlightedSegment: "B2-B3",
        faultySensors: [],
        activeAnomalies: [
          { sensor_id: "B2", type: "PRESSURE_ANOMALY", severity: "HIGH" }
        ],
        incidents: liveHardwareIncident ? [liveHardwareIncident] : [],
        aiAnalysis: {
          whyDetected: [
            `Physical FSR402 force-input simulator on ESP32 (GPIO34) registered raw ADC ${hardwareState.telemetry?.raw_value} exceeding threshold (${hardwareState.telemetry?.threshold}).`,
            "Pipeline anomaly detector identified spatial pressure drop on Node B2 (Segment B2-B3)."
          ],
          recommendedActions: [
            "Inspect physical pipeline segment B2-B3 for high pressure drop / burst.",
            "Verify ESP32 hardware telemetry stream and local GPIO32 buzzer status.",
            "Check downstream pressure recovery at Node B3."
          ],
          confidenceNote: "Model confidence: 92%. Spatial correlation across responsive sensors B2 and B3.",
          limitations: "FSR402 is a prototype force-input simulator. Derived flow loss is a model compatibility calculation."
        }
      };
    } else {
      effectiveState = {
        scenario: "normal",
        networkStatus: {
          total_sensors: 10,
          healthy_sensors: 10,
          degraded_sensors: 0,
          faulty_sensors: 0,
          active_anomalies: 0,
          active_leaks: 0,
          estimated_total_loss_lpm: 0,
          network_status: "HEALTHY"
        },
        highlightedSegment: null,
        faultySensors: [],
        activeAnomalies: [],
        incidents: [],
        aiAnalysis: SCENARIO_STATES["normal"].aiAnalysis
      };
    }
  }

  // Combine live active incidents with all persistent backend historical incidents
  const allIncidentsMap = new Map<string, Incident>();

  // Add backend history first
  backendIncidents.forEach((inc) => allIncidentsMap.set(inc.incident_id, inc));

  // If live hardware incident exists, place it in map
  if (liveHardwareIncident) {
    allIncidentsMap.set(liveHardwareIncident.incident_id, liveHardwareIncident);
  }

  // If demo state incidents exist, place in map
  demoState.incidents.forEach((inc) => {
    if (!allIncidentsMap.has(inc.incident_id)) {
      allIncidentsMap.set(inc.incident_id, inc);
    }
  });

  const combinedIncidents = Array.from(allIncidentsMap.values()).sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );

  return (
    <DemoContext.Provider
      value={{
        scenario,
        setScenario,
        isBackendLive,
        isDemoMode,
        setIsDemoMode,
        isHardwareLive,
        hardwareState,
        activeState: {
          ...effectiveState,
          incidents: isHardwareAlert && liveHardwareIncident ? [liveHardwareIncident] : demoState.incidents
        },
        incidents: combinedIncidents,
        acknowledgeIncident,
        resolveIncident,
        refreshBackendData
      }}
    >
      {children}
    </DemoContext.Provider>
  );
};

export const useDemo = () => {
  const context = useContext(DemoContext);
  if (!context) {
    throw new Error("useDemo must be used within a DemoProvider");
  }
  return context;
};
