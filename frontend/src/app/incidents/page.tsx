"use client";

import React, { useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/layout/AppShell";
import { useDemo } from "@/context/DemoContext";
import { AlertTriangle, Filter, ChevronRight, CheckCircle2, Cpu, Database } from "lucide-react";

export default function IncidentsListPage() {
  const { incidents, acknowledgeIncident, resolveIncident, hardwareState } = useDemo();
  const [statusFilter, setStatusFilter] = useState<string>("ALL");
  const [severityFilter, setSeverityFilter] = useState<string>("ALL");
  const [sourceFilter, setSourceFilter] = useState<string>("ALL");

  const isHardwareAlertActive =
    hardwareState.connection_state === "LIVE HARDWARE" && hardwareState.telemetry?.status === "ALERT";

  const filteredIncidents = incidents.filter((inc) => {
    if (statusFilter !== "ALL" && inc.status !== statusFilter) return false;
    if (severityFilter !== "ALL" && inc.severity !== severityFilter) return false;
    if (sourceFilter !== "ALL") {
      const isHw =
        inc.source === "LIVE HARDWARE" ||
        inc.incident_id.startsWith("INC-HW") ||
        inc.incident_id.startsWith("INC-ESP32") ||
        inc.disclaimer?.includes("FSR402");
      if (sourceFilter === "LIVE_HARDWARE" && !isHw) return false;
      if (sourceFilter === "SIMULATION" && isHw) return false;
    }
    return true;
  });

  return (
    <AppShell>
      <div className="p-6 max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 border-b border-slate-800 gap-4">
          <div>
            <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-rose-500" />
              Persisted Pipeline Incidents
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Historical & active leak incidents persisted in SQLite/PostgreSQL database layer
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {/* Source Filter */}
            <div className="flex items-center gap-1.5 bg-[#0f172a] p-1 rounded-lg border border-slate-800 text-xs">
              <Filter className="w-3.5 h-3.5 text-slate-400 ml-2" />
              <span className="text-slate-400 font-semibold">Source:</span>
              {(["ALL", "LIVE_HARDWARE", "SIMULATION"] as const).map((src) => (
                <button
                  key={src}
                  onClick={() => setSourceFilter(src)}
                  className={`px-2 py-1 rounded font-medium transition ${
                    sourceFilter === src ? "bg-cyan-500 text-slate-950 font-bold" : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  {src.replace("_", " ")}
                </button>
              ))}
            </div>

            {/* Status Filter */}
            <div className="flex items-center gap-1.5 bg-[#0f172a] p-1 rounded-lg border border-slate-800 text-xs">
              <span className="text-slate-400 font-semibold ml-2">Status:</span>
              {(["ALL", "OPEN", "ACKNOWLEDGED", "RESOLVED"] as const).map((st) => (
                <button
                  key={st}
                  onClick={() => setStatusFilter(st)}
                  className={`px-2 py-1 rounded font-medium transition ${
                    statusFilter === st ? "bg-cyan-500 text-slate-950 font-bold" : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  {st}
                </button>
              ))}
            </div>

            {/* Severity Filter */}
            <div className="flex items-center gap-1.5 bg-[#0f172a] p-1 rounded-lg border border-slate-800 text-xs">
              <span className="text-slate-400 font-semibold ml-2">Severity:</span>
              {(["ALL", "LOW", "MEDIUM", "HIGH", "CRITICAL"] as const).map((sev) => (
                <button
                  key={sev}
                  onClick={() => setSeverityFilter(sev)}
                  className={`px-2 py-1 rounded font-medium transition ${
                    severityFilter === sev ? "bg-cyan-500 text-slate-950 font-bold" : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  {sev}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Incident List Table / Cards */}
        {filteredIncidents.length === 0 ? (
          <div className="bg-[#0f172a] border border-slate-800 rounded-xl p-12 text-center space-y-3">
            <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto" />
            <h3 className="text-base font-bold text-white">No Incidents Found</h3>
            <p className="text-xs text-slate-400 max-w-md mx-auto">
              There are currently no persisted incidents matching your active filter parameters.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredIncidents.map((inc) => {
              const isHardware =
                inc.source === "LIVE HARDWARE" ||
                inc.incident_id.startsWith("INC-HW") ||
                inc.incident_id.startsWith("INC-ESP32") ||
                inc.disclaimer?.includes("FSR402");

              const isCurrentlyActiveAlert = isHardwareAlertActive && inc.status !== "RESOLVED";

              return (
                <div
                  key={inc.incident_id}
                  className="bg-[#0f172a] border border-slate-800 hover:border-cyan-500/40 rounded-xl p-5 shadow-md transition flex flex-col md:flex-row items-start md:items-center justify-between gap-4"
                >
                  <div className="space-y-2 flex-1">
                    <div className="flex flex-wrap items-center gap-2.5">
                      <span
                        className={`px-2.5 py-0.5 rounded text-xs font-bold font-mono ${
                          inc.severity === "CRITICAL"
                            ? "bg-rose-500/20 text-rose-300 border border-rose-500/40"
                            : inc.severity === "HIGH"
                            ? "bg-amber-500/20 text-amber-300 border border-amber-500/40"
                            : "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40"
                        }`}
                      >
                        {inc.severity}
                      </span>
                      <h3 className="font-bold text-white text-base">{inc.incident_type.replace("_", " ")}</h3>
                      <span className="text-xs text-slate-400 font-mono">ID: {inc.incident_id}</span>

                      {/* Source Badge */}
                      <span
                        className={`inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded font-mono font-medium ${
                          isHardware
                            ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"
                            : "bg-amber-500/10 text-amber-300 border border-amber-500/30"
                        }`}
                      >
                        {isHardware ? (
                          <>
                            <Cpu className="w-3 h-3 text-emerald-400" /> LIVE HARDWARE (ESP32)
                          </>
                        ) : (
                          <>
                            <Database className="w-3 h-3 text-amber-300" /> SIMULATION ENGINE
                          </>
                        )}
                      </span>
                    </div>

                    <div className="flex flex-wrap items-center gap-6 text-xs text-slate-300">
                      <div>
                        Segment: <span className="font-bold text-white font-mono">{inc.affected_segment}</span> ({inc.affected_zone})
                      </div>
                      <div>
                        Confidence: <span className="font-bold text-cyan-400 font-mono">{(inc.confidence * 100).toFixed(1)}%</span>
                      </div>
                      <div>
                        Est. Flow Loss: <span className="font-bold text-white font-mono">{inc.estimated_flow_loss_lpm} LPM</span>
                      </div>
                      {inc.peak_raw_adc != null && (
                        <div>
                          Peak Raw ADC: <span className="font-bold text-emerald-400 font-mono">{inc.peak_raw_adc}</span>
                        </div>
                      )}
                      {inc.peak_pressure_equivalent != null && (
                        <div>
                          Pressure Eq: <span className="font-bold text-emerald-400 font-mono">{inc.peak_pressure_equivalent.toFixed(1)}%</span>
                        </div>
                      )}
                    </div>

                    <div className="flex flex-wrap items-center gap-4 text-[11px] text-slate-400 font-mono">
                      <span>Created: {inc.created_at ? new Date(inc.created_at).toLocaleString() : "N/A"}</span>
                      {inc.acknowledged_at && (
                        <span className="text-amber-400">Ack: {new Date(inc.acknowledged_at).toLocaleString()}</span>
                      )}
                      {inc.resolved_at && (
                        <span className="text-emerald-400">Res: {new Date(inc.resolved_at).toLocaleString()}</span>
                      )}
                    </div>

                    <p className="text-xs text-slate-400 italic">
                      {inc.evidence[0] || "Topology correlation confirmed across responsive sensors."}
                    </p>
                  </div>

                  {/* Right Action Bar */}
                  <div className="flex items-center gap-3 w-full md:w-auto border-t md:border-t-0 border-slate-800 pt-3 md:pt-0">
                    <span
                      className={`px-3 py-1 rounded text-xs font-bold font-mono ${
                        inc.status === "OPEN"
                          ? "bg-rose-500/20 text-rose-300 border border-rose-500/30 animate-pulse"
                          : inc.status === "ACKNOWLEDGED"
                          ? "bg-amber-500/20 text-amber-300 border border-amber-500/30"
                          : "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                      }`}
                    >
                      {inc.status}
                    </span>

                    {inc.status === "OPEN" && (
                      <button
                        onClick={() => acknowledgeIncident(inc.incident_id)}
                        className="bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold px-3 py-1.5 rounded text-xs transition"
                      >
                        ACKNOWLEDGE
                      </button>
                    )}

                    {inc.status !== "RESOLVED" && (
                      <button
                        disabled={isCurrentlyActiveAlert}
                        onClick={() => resolveIncident(inc.incident_id)}
                        className={`font-bold px-3 py-1.5 rounded text-xs transition ${
                          isCurrentlyActiveAlert
                            ? "bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700"
                            : "bg-emerald-500 hover:bg-emerald-400 text-slate-950"
                        }`}
                        title={
                          isCurrentlyActiveAlert
                            ? "Resolve after sensor returns to NORMAL"
                            : "Close and resolve historical incident"
                        }
                      >
                        RESOLVE
                      </button>
                    )}

                    <Link
                      href={`/incidents/${inc.incident_id}`}
                      className="inline-flex items-center gap-1 bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-1.5 rounded text-xs border border-slate-700 font-semibold transition"
                    >
                      <span>INVESTIGATE</span>
                      <ChevronRight className="w-3.5 h-3.5" />
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </AppShell>
  );
}

