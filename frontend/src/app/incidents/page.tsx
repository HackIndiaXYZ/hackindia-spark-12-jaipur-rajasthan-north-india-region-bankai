"use client";

import React, { useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/layout/AppShell";
import { useDemo } from "@/context/DemoContext";
import { AlertTriangle, Filter, ChevronRight, Eye, CheckCircle2 } from "lucide-react";
import { IncidentStatus, IncidentSeverity } from "@/types";

export default function IncidentsListPage() {
  const { incidents, acknowledgeIncident, resolveIncident } = useDemo();
  const [statusFilter, setStatusFilter] = useState<string>("ALL");
  const [severityFilter, setSeverityFilter] = useState<string>("ALL");

  const filteredIncidents = incidents.filter((inc) => {
    if (statusFilter !== "ALL" && inc.status !== statusFilter) return false;
    if (severityFilter !== "ALL" && inc.severity !== severityFilter) return false;
    return true;
  });

  return (
    <AppShell>
      <div className="p-6 max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div>
            <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-rose-500" />
              Persisted Pipeline Incidents
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Historical & active leak incidents persisted in SQLite/PostgreSQL database layer
            </p>
          </div>

          <div className="flex items-center gap-3">
            {/* Status Filter */}
            <div className="flex items-center gap-1.5 bg-[#0f172a] p-1 rounded-lg border border-slate-800 text-xs">
              <Filter className="w-3.5 h-3.5 text-slate-400 ml-2" />
              <span className="text-slate-400 font-semibold">Status:</span>
              {(["ALL", "OPEN", "ACKNOWLEDGED", "RESOLVED"] as const).map((st) => (
                <button
                  key={st}
                  onClick={() => setStatusFilter(st)}
                  className={`px-2.5 py-1 rounded font-medium transition ${
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
                  className={`px-2.5 py-1 rounded font-medium transition ${
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
            {filteredIncidents.map((inc) => (
              <div
                key={inc.incident_id}
                className="bg-[#0f172a] border border-slate-800 hover:border-cyan-500/40 rounded-xl p-5 shadow-md transition flex flex-col md:flex-row items-start md:items-center justify-between gap-4"
              >
                <div className="space-y-2">
                  <div className="flex items-center gap-3">
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
                    <h3 className="font-bold text-white text-base">{inc.incident_type}</h3>
                    <span className="text-xs text-slate-400 font-mono">ID: {inc.incident_id}</span>
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
                    <div>
                      Est. Volume Loss: <span className="font-bold text-white font-mono">{inc.estimated_volume_loss_liters} L</span>
                    </div>
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
                        ? "bg-rose-500/20 text-rose-300 border border-rose-500/30"
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
                      onClick={() => resolveIncident(inc.incident_id)}
                      className="bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold px-3 py-1.5 rounded text-xs transition"
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
            ))}
          </div>
        )}
      </div>
    </AppShell>
  );
}
