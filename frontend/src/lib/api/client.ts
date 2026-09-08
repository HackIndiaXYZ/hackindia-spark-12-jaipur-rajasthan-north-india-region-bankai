import {
  NetworkStatus,
  NetworkTopology,
  Incident,
  GovernmentDataSource,
  GovernmentObservationSummary,
  GovernmentObservation,
  SensorReading
} from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api";

export async function checkBackendHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE_URL}/health`, { cache: "no-store" });
    return res.ok;
  } catch (_err) {
    return false;
  }
}

export async function getNetworkStatus(): Promise<NetworkStatus> {
  const res = await fetch(`${API_BASE_URL}/network`, { cache: "no-store" });
  if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to fetch network status`);
  return res.json();
}

export async function getNetworkTopology(): Promise<NetworkTopology> {
  const res = await fetch(`${API_BASE_URL}/network/topology`, { cache: "no-store" });
  if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to fetch network topology`);
  return res.json();
}

export async function listIncidents(
  status?: string,
  severity?: string,
  limit: number = 50,
  offset: number = 0
): Promise<Incident[]> {
  const params = new URLSearchParams();
  if (status) params.append("status", status);
  if (severity) params.append("severity", severity);
  params.append("limit", limit.toString());
  params.append("offset", offset.toString());

  const res = await fetch(`${API_BASE_URL}/incidents?${params.toString()}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to list incidents`);
  return res.json();
}

export async function getIncidentById(incidentId: string): Promise<Incident> {
  const res = await fetch(`${API_BASE_URL}/incidents/${incidentId}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to fetch incident ${incidentId}`);
  return res.json();
}

export async function updateIncidentStatus(incidentId: string, status: "ACKNOWLEDGED" | "RESOLVED"): Promise<Incident> {
  const res = await fetch(`${API_BASE_URL}/incidents/${incidentId}/status`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status })
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: "Failed to update incident status" }));
    throw new Error(errorData.detail || `HTTP ${res.status}: Failed to update status`);
  }
  return res.json();
}

export async function analyzeTelemetry(readings: SensorReading[]): Promise<Incident | null> {
  const res = await fetch(`${API_BASE_URL}/incidents/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(readings)
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to analyze telemetry`);
  return res.json();
}

export async function listDataSources(): Promise<{ sources: GovernmentDataSource[]; total_count: number }> {
  const res = await fetch(`${API_BASE_URL}/data-sources`, { cache: "no-store" });
  if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to fetch data sources`);
  return res.json();
}

export async function getDataSource(sourceId: string): Promise<GovernmentDataSource> {
  const res = await fetch(`${API_BASE_URL}/data-sources/${sourceId}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to fetch data source ${sourceId}`);
  return res.json();
}

export async function getDataSourceSummary(sourceId: string): Promise<GovernmentObservationSummary> {
  const res = await fetch(`${API_BASE_URL}/data-sources/${sourceId}/summary`, { cache: "no-store" });
  if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to fetch data source summary for ${sourceId}`);
  return res.json();
}

export async function getRecentObservations(
  sourceId: string,
  limit: number = 50
): Promise<{ source_id: string; observations: GovernmentObservation[]; total_returned: number }> {
  const res = await fetch(`${API_BASE_URL}/data-sources/${sourceId}/recent?limit=${limit}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to fetch recent observations for ${sourceId}`);
  return res.json();
}

export async function getAIAnalysis(incidentId: string): Promise<{
  incident_id: string;
  analysis: {
    summary: string;
    why_detected: string[];
    recommended_actions: string[];
    confidence_note: string;
    limitations: string;
  };
  provider: string;
}> {
  const res = await fetch(`${API_BASE_URL}/incidents/${incidentId}/ai-analysis`, {
    method: "POST",
    headers: { "Content-Type": "application/json" }
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to fetch AI analysis for ${incidentId}`);
  return res.json();
}

