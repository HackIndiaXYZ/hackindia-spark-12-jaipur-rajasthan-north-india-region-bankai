import {
  NetworkStatus,
  NetworkTopology,
  Incident,
  GovernmentDataSource,
  GovernmentObservationSummary,
  GovernmentObservation,
  SensorReading
} from "@/types";

export function getApiBaseUrl(): string {
  const raw = process.env.NEXT_PUBLIC_API_BASE_URL || "https://aquasentinel-api-r00y.onrender.com";
  let clean = raw.trim().replace(/\/+$/, "");
  if (clean.endsWith("/api")) {
    clean = clean.slice(0, -4);
  }
  return clean;
}

export function getApiEndpoint(endpointPath: string): string {
  const base = getApiBaseUrl();
  const cleanPath = endpointPath.startsWith("/") ? endpointPath : `/${endpointPath}`;
  if (cleanPath.startsWith("/api/")) {
    return `${base}${cleanPath}`;
  }
  return `${base}/api${cleanPath}`;
}

export function getApiHostLabel(): string {
  const base = getApiBaseUrl();
  if (base.includes("onrender.com") || base.includes("aquasentinel-api")) {
    return "Render Cloud API";
  }
  if (base.includes("localhost") || base.includes("127.0.0.1")) {
    return "Localhost API (Port 8000)";
  }
  try {
    const url = new URL(base);
    return url.hostname;
  } catch (_e) {
    return base;
  }
}

export const API_BASE_URL = getApiEndpoint("");

export async function checkBackendHealth(): Promise<boolean> {
  try {
    const res = await fetch(getApiEndpoint("/health"), { cache: "no-store" });
    return res.ok;
  } catch (_err) {
    return false;
  }
}

export async function getNetworkStatus(): Promise<NetworkStatus> {
  const res = await fetch(getApiEndpoint("/network"), { cache: "no-store" });
  if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to fetch network status`);
  return res.json();
}

export async function getNetworkTopology(): Promise<NetworkTopology> {
  const res = await fetch(getApiEndpoint("/network/topology"), { cache: "no-store" });
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

  const res = await fetch(`${getApiEndpoint("/incidents")}?${params.toString()}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to list incidents`);
  return res.json();
}

export async function getIncidentById(incidentId: string): Promise<Incident> {
  const res = await fetch(getApiEndpoint(`/incidents/${incidentId}`), { cache: "no-store" });
  if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to fetch incident ${incidentId}`);
  return res.json();
}

export async function updateIncidentStatus(incidentId: string, status: "ACKNOWLEDGED" | "RESOLVED"): Promise<Incident> {
  const res = await fetch(getApiEndpoint(`/incidents/${incidentId}/status`), {
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
  const res = await fetch(getApiEndpoint("/incidents/analyze"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(readings)
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to analyze telemetry`);
  return res.json();
}

export async function listDataSources(): Promise<{ sources: GovernmentDataSource[]; total_count: number }> {
  const res = await fetch(getApiEndpoint("/data-sources"), { cache: "no-store" });
  if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to fetch data sources`);
  return res.json();
}

export async function getDataSource(sourceId: string): Promise<GovernmentDataSource> {
  const res = await fetch(getApiEndpoint(`/data-sources/${sourceId}`), { cache: "no-store" });
  if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to fetch data source ${sourceId}`);
  return res.json();
}

export async function getDataSourceSummary(sourceId: string): Promise<GovernmentObservationSummary> {
  const res = await fetch(getApiEndpoint(`/data-sources/${sourceId}/summary`), { cache: "no-store" });
  if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to fetch data source summary for ${sourceId}`);
  return res.json();
}

export async function getRecentObservations(
  sourceId: string,
  limit: number = 50
): Promise<{ source_id: string; observations: GovernmentObservation[]; total_returned: number }> {
  const res = await fetch(`${getApiEndpoint(`/data-sources/${sourceId}/recent`)}?limit=${limit}`, { cache: "no-store" });
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
  const res = await fetch(getApiEndpoint(`/incidents/${incidentId}/ai-analysis`), {
    method: "POST",
    headers: { "Content-Type": "application/json" }
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to fetch AI analysis for ${incidentId}`);
  return res.json();
}
