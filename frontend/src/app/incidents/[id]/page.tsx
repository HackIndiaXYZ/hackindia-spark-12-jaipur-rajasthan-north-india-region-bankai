"use client";

import React, { use } from "react";
import Link from "next/link";
import { AppShell } from "@/components/layout/AppShell";
import { AIAnalysisPanel } from "@/components/incidents/AIAnalysisPanel";
import { useDemo } from "@/context/DemoContext";
import {
  AlertTriangle,
  ArrowLeft,
  CheckCircle2,
  Clock,
  Eye,
  Crosshair,
  TrendingDown,
  ShieldAlert,
  Info,
  Radio
} from "lucide-react";
import { DEMO_INCIDENTS } from "@/lib/demo/demoData";

export default function IncidentDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { incidents, acknowledgeIncident, resolveIncident, activeState } = useDemo();

  // Find incident in live context, or fallback to DEMO_INCIDENTS
  const incident =
    incidents.find((i) => i.incident_id === id) ||
    Object.values(DEMO_INCIDENTS).find((i) => i.incident_id === id) ||
    DEMO_INCIDENTS["INC-GRADUAL-LEAK"];

  return (
    <AppShell>
      <div className="p-6 max-w-7xl mx-auto space-y-6">
        {/* Back Button & Header */}
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
          <div className="flex items-center gap-4">
            <Link
              href="/incidents"
              className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg border border-slate-700 transition"
            >
              <ArrowLeft className="w-4 h-4" />
            </Link>
            <div>
              <div className="flex items-center gap-3">
                <h1 className="text-xl font-bold text-white tracking-tight">{incident.incident_type}</h1>
                <span className="text-xs font-mono text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/30">
                  ID: {incident.incident_id}
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-1">
                Detected at {incident.detected_at} (Fingerprint: {incident.fingerprint})
              </p>
            </div>
          </div>

          {/* Lifecycle Status & Actions */}
          <div className="flex items-center gap-3">
            <span
              className={`px-3 py-1 rounded text-xs font-bold font-mono ${
                incident.status === "OPEN"
                  ? "bg-rose-500/20 text-rose-300 border border-rose-500/40"
                  : incident.status === "ACKNOWLEDGED"
                  ? "bg-amber-500/20 text-amber-300 border border-amber-500/40"
                  : "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
              }`}
            >
              STATUS: {incident.status}
            </span>

            {incident.status === "OPEN" && (
              <button
                onClick={() => acknowledgeIncident(incident.incident_id)}
                className="bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold px-4 py-1.5 rounded text-xs transition"
              >
                ACKNOWLEDGE
              </button>
            )}

            {incident.status !== "RESOLVED" && (
              <button
                onClick={() => resolveIncident(incident.incident_id)}
                className="bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold px-4 py-1.5 rounded text-xs transition"
              >
                RESOLVE
              </button>
            )}
          </div>
        </div>

        {/* STATS GRID (7 Key Metrics) */}
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
          <div className="bg-[#0f172a] p-3 rounded-lg border border-slate-800">
            <span className="text-[11px] text-slate-400 uppercase tracking-wider block mb-1">Affected Segment</span>
            <span className="text-base font-bold text-rose-400 font-mono">{incident.affected_segment}</span>
          </div>

          <div className="bg-[#0f172a] p-3 rounded-lg border border-slate-800">
            <span className="text-[11px] text-slate-400 uppercase tracking-wider block mb-1">Affected Zone</span>
            <span className="text-base font-bold text-white font-mono">{incident.affected_zone}</span>
          </div>

          <div className="bg-[#0f172a] p-3 rounded-lg border border-slate-800">
            <span className="text-[11px] text-slate-400 uppercase tracking-wider block mb-1">Confidence Score</span>
            <span className="text-base font-bold text-cyan-400 font-mono">{(incident.confidence * 100).toFixed(1)}%</span>
          </div>

          <div className="bg-[#0f172a] p-3 rounded-lg border border-slate-800">
            <span className="text-[11px] text-slate-400 uppercase tracking-wider block mb-1">Observability</span>
            <span className="text-base font-bold text-indigo-400 font-mono">{(incident.observability_score * 100).toFixed(1)}%</span>
          </div>

          <div className="bg-[#0f172a] p-3 rounded-lg border border-slate-800">
            <span className="text-[11px] text-slate-400 uppercase tracking-wider block mb-1">Detection Delay</span>
            <span className="text-base font-bold text-amber-400 font-mono">{incident.detection_delay_min} min</span>
          </div>

          <div className="bg-[#0f172a] p-3 rounded-lg border border-slate-800">
            <span className="text-[11px] text-slate-400 uppercase tracking-wider block mb-1">Est. Flow Loss</span>
            <span className="text-base font-bold text-white font-mono">{incident.estimated_flow_loss_lpm} LPM</span>
          </div>

          <div className="bg-[#0f172a] p-3 rounded-lg border border-slate-800">
            <span className="text-[11px] text-slate-400 uppercase tracking-wider block mb-1">Est. Volume Loss</span>
            <span className="text-base font-bold text-white font-mono">{incident.estimated_volume_loss_liters} L</span>
          </div>
        </div>

        {/* EVIDENCE & LOCALIZATION ROW */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Evidence Panel */}
          <div className="bg-[#0f172a] border border-slate-800 rounded-xl p-5 shadow-md space-y-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Radio className="w-4 h-4 text-cyan-400" />
              Structured System Evidence
            </h3>

            <div className="space-y-2">
              {incident.evidence.map((item, idx) => (
                <div key={idx} className="p-3 bg-[#0b0f19] rounded-lg border border-slate-800 text-xs text-slate-300 flex items-start gap-2.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 mt-1.5 flex-shrink-0"></span>
                  <span className="leading-relaxed">{item}</span>
                </div>
              ))}
            </div>

            <div className="p-3 bg-cyan-500/5 rounded border border-cyan-500/20 text-xs text-slate-400">
              <span className="font-semibold text-cyan-300 block mb-0.5">Responsive Sensors:</span>
              <div className="flex flex-wrap gap-1.5 mt-1">
                {incident.responsive_sensors.map((sensor) => (
                  <span key={sensor} className="bg-cyan-950 text-cyan-300 border border-cyan-800 px-2 py-0.5 rounded font-mono text-[11px]">
                    Sensor {sensor}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Candidate Localization Panel */}
          <div className="bg-[#0f172a] border border-slate-800 rounded-xl p-5 shadow-md space-y-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center justify-between">
              <span className="flex items-center gap-2">
                <Crosshair className="w-4 h-4 text-rose-400" />
                Candidate Segment Localization
              </span>
              <span className="text-[10px] text-slate-400 font-mono">TOPOLOGY AWARE</span>
            </h3>

            <div className="space-y-3">
              <div className="p-3 bg-[#0b0f19] rounded-lg border border-rose-500/40">
                <div className="flex justify-between items-center mb-1">
                  <span className="text-xs font-bold text-white">Primary Affected Segment: {incident.affected_segment}</span>
                  <span className="text-xs font-mono font-bold text-rose-400">{(incident.confidence * 100).toFixed(1)}%</span>
                </div>
                <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mt-2">
                  <div className="bg-rose-500 h-full rounded-full" style={{ width: `${incident.confidence * 100}%` }}></div>
                </div>
              </div>

              <div className="space-y-2">
                <span className="text-xs font-semibold text-slate-400">Other Candidate Segments:</span>
                {incident.candidate_segments.map((cand, idx) => (
                  <div key={idx} className="p-2.5 bg-[#0b0f19] rounded border border-slate-800 text-xs flex items-center justify-between">
                    <div>
                      <span className="font-bold text-slate-200 font-mono">{cand.segment_id}</span>
                      <span className="text-[11px] text-slate-400 block">{cand.reason}</span>
                    </div>
                    <span className="font-mono text-slate-300 font-bold">{(cand.confidence * 100).toFixed(0)}%</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* AI ANALYSIS PANEL */}
        <AIAnalysisPanel
          whyDetected={activeState.aiAnalysis.whyDetected}
          recommendedActions={activeState.aiAnalysis.recommendedActions}
          confidenceNote={activeState.aiAnalysis.confidenceNote}
          limitations={incident.disclaimer}
        />
      </div>
    </AppShell>
  );
}
