"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { ScenarioType, Incident } from "@/types";
import { CANONICAL_TOPOLOGY, SCENARIO_STATES, ScenarioDemoState, generateScenarioReadings } from "@/lib/demo/demoData";
import { checkBackendHealth, getNetworkStatus, listIncidents, updateIncidentStatus, analyzeTelemetry } from "@/lib/api/client";

interface DemoContextType {
  scenario: ScenarioType;
  setScenario: (scenario: ScenarioType) => void;
  isBackendLive: boolean;
  isDemoMode: boolean;
  setIsDemoMode: (val: boolean) => void;
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
  const [isDemoMode, setIsDemoMode] = useState<boolean>(true); // Default to Demo Mode for hackathon demo stability
  const [demoState, setDemoState] = useState<ScenarioDemoState>(SCENARIO_STATES["normal"]);
  const [backendIncidents, setBackendIncidents] = useState<Incident[]>([]);

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

  // Handle scenario switching
  const setScenario = useCallback(async (newScenario: ScenarioType) => {
    setScenarioState(newScenario);
    const targetState = JSON.parse(JSON.stringify(SCENARIO_STATES[newScenario])) as ScenarioDemoState;
    setDemoState(targetState);

    // If backend is live and we trigger a scenario, analyze telemetry via real backend API
    if (isBackendLive && !isDemoMode) {
      try {
        const readings = generateScenarioReadings(newScenario);
        const result = await analyzeTelemetry(readings);
        const realList = await listIncidents();
        setBackendIncidents(realList);
      } catch (err) {
        console.warn("Failed to submit telemetry to backend:", err);
      }
    }
  }, [isBackendLive, isDemoMode]);

  // Fetch backend data if real backend mode is active
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

  useEffect(() => {
    if (!isDemoMode && isBackendLive) {
      refreshBackendData();
    }
  }, [isDemoMode, isBackendLive, refreshBackendData]);

  // Acknowledge incident handler
  const acknowledgeIncident = async (id: string) => {
    if (isBackendLive && !isDemoMode) {
      try {
        await updateIncidentStatus(id, "ACKNOWLEDGED");
        await refreshBackendData();
        return;
      } catch (err) {
        console.warn("Backend update failed, falling back to local state:", err);
      }
    }

    // Local state update
    setDemoState((prev) => {
      const updatedIncidents = prev.incidents.map((inc) =>
        inc.incident_id === id ? { ...inc, status: "ACKNOWLEDGED" as const } : inc
      );
      return { ...prev, incidents: updatedIncidents };
    });
  };

  // Resolve incident handler
  const resolveIncident = async (id: string) => {
    if (isBackendLive && !isDemoMode) {
      try {
        await updateIncidentStatus(id, "RESOLVED");
        await refreshBackendData();
        return;
      } catch (err) {
        console.warn("Backend update failed, falling back to local state:", err);
      }
    }

    // Local state update
    setDemoState((prev) => {
      const updatedIncidents = prev.incidents.map((inc) =>
        inc.incident_id === id ? { ...inc, status: "RESOLVED" as const } : inc
      );

      // When resolved, clear highlighted segment & return network status to healthy
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

  const activeIncidents = isDemoMode || !isBackendLive ? demoState.incidents : backendIncidents;

  return (
    <DemoContext.Provider
      value={{
        scenario,
        setScenario,
        isBackendLive,
        isDemoMode,
        setIsDemoMode,
        activeState: {
          ...demoState,
          incidents: activeIncidents
        },
        incidents: activeIncidents,
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
