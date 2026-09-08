"use client";

import React, { useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/layout/AppShell";
import { NetworkTopologyMap } from "@/components/network/NetworkTopologyMap";
import { AIAnalysisPanel } from "@/components/incidents/AIAnalysisPanel";
import { useDemo } from "@/context/DemoContext";
import { CANONICAL_TOPOLOGY } from "@/lib/demo/demoData";
import {
  Activity,
  AlertTriangle,
  Radio,
  Eye,
  TrendingDown,
  ShieldCheck,
  CheckCircle2,
  Play,
  ArrowRight,
  Sparkles,
  Info,
  ChevronRight
} from "lucide-react";
import { ScenarioType } from "@/types";

export default function DashboardPage() {
  const {
    scenario,
    setScenario,
    activeState,
    incidents,
    acknowledgeIncident,
    resolveIncident,
    isDemoMode
  } = useDemo();

  const [selectedSegment, setSelectedSegment] = useState<string | null>(null);
  const [selectedSensor, setSelectedSensor] = useState<string | null>(null);

  const activeIncident = incidents.length > 0 ? incidents[0] : null;

  return (
    <AppShell>
      <div className="p-6 space-y-6 max-w-[1600px] mx-auto">
        {/* Top Control Room Banner */}
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 bg-[#0f172a] p-5 rounded-xl border border-slate-800 shadow-md">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <h1 className="text-xl font-bold text-white tracking-tight">Operational Command Console</h1>
              <span className="text-[10px] bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 px-2 py-0.5 rounded font-mono">
                LIVE DEMO CONTROL
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Real-time water pipeline telemetry, topology localization, simulated observability & false alarm intelligence
            </p>
          </div>

          {/* Quick Scenario Trigger Selector */}
          <div className="flex items-center gap-2 bg-[#0b0f19] p-1.5 rounded-lg border border-slate-800">
            <span className="text-xs font-semibold text-slate-400 px-2 flex items-center gap-1.5">
              <Play className="w-3.5 h-3.5 text-cyan-400" /> Trigger Scenario:
            </span>
            {(["normal", "gradual_leak", "sudden_burst", "sensor_fault"] as ScenarioType[]).map((sc) => (
              <button
                key={sc}
                onClick={() => setScenario(sc)}
                className={`px-3 py-1.5 rounded text-xs font-semibold transition ${
                  scenario === sc
                    ? "bg-cyan-500 text-slate-950 shadow-[0_0_10px_rgba(6,182,212,0.4)]"
                    : "text-slate-300 hover:text-white hover:bg-slate-800"
                }`}
              >
                {sc === "normal" && "A: Normal"}
                {sc === "gradual_leak" && "B: Leak (B2-B3)"}
                {sc === "sudden_burst" && "C: Burst (Zone B)"}
                {sc === "sensor_fault" && "D: Sensor Fault (B3)"}
              </button>
            ))}
          </div>
        </div>

        {/* TOP KPI ROW (5 Cards) */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          {/* 1. Network Observability Index (Visually Prominent Differentiator) */}
          <div className="bg-gradient-to-br from-[#0f172a] to-[#1e1b4b] p-4 rounded-xl border border-indigo-500/30 shadow-lg relative overflow-hidden">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-indigo-300 uppercase tracking-wider">
                Observability Index
              </span>
              <Eye className="w-4 h-4 text-indigo-400" />
            </div>
            <div className="text-3xl font-black text-white font-mono">
              {(activeState.networkStatus.network_status === "HEALTHY" ? 89.7 : 91.0).toFixed(1)}%
            </div>
            <p className="text-[10px] text-indigo-300/80 mt-1">
              Model-derived simulated coverage index
            </p>
          </div>

          {/* 2. Active Incidents */}
          <div className="bg-[#0f172a] p-4 rounded-xl border border-slate-800 shadow-md">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                Active Incidents
              </span>
              <AlertTriangle className={`w-4 h-4 ${incidents.length > 0 ? "text-rose-400" : "text-slate-500"}`} />
            </div>
            <div className={`text-3xl font-black font-mono ${incidents.length > 0 ? "text-rose-400" : "text-slate-200"}`}>
              {incidents.length}
            </div>
            <p className="text-[10px] text-slate-400 mt-1">
              {incidents.length > 0 ? `${incidents[0].severity} Severity (${incidents[0].affected_segment})` : "No active pipeline incidents"}
            </p>
          </div>

          {/* 3. Sensors Online */}
          <div className="bg-[#0f172a] p-4 rounded-xl border border-slate-800 shadow-md">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                Sensors Online
              </span>
              <Radio className="w-4 h-4 text-cyan-400" />
            </div>
            <div className="text-3xl font-black text-white font-mono">
              {activeState.networkStatus.healthy_sensors} / {activeState.networkStatus.total_sensors}
            </div>
            <p className="text-[10px] text-slate-400 mt-1">
              {activeState.faultySensors.length > 0 ? `Faulty: ${activeState.faultySensors.join(", ")}` : "10/10 Sensors Normal"}
            </p>
          </div>

          {/* 4. Active Anomalies */}
          <div className="bg-[#0f172a] p-4 rounded-xl border border-slate-800 shadow-md">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                Active Anomalies
              </span>
              <Activity className="w-4 h-4 text-amber-400" />
            </div>
            <div className="text-3xl font-black text-amber-400 font-mono">
              {activeState.activeAnomalies.length}
            </div>
            <p className="text-[10px] text-slate-400 mt-1">
              {scenario === "sensor_fault" ? "1 Isolated Sensor Fault" : `${activeState.activeAnomalies.length} Pressure/Flow variance`}
            </p>
          </div>

          {/* 5. Estimated Flow Loss */}
          <div className="bg-[#0f172a] p-4 rounded-xl border border-slate-800 shadow-md">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                Estimated Flow Loss
              </span>
              <TrendingDown className="w-4 h-4 text-rose-400" />
            </div>
            <div className="text-3xl font-black text-white font-mono">
              {activeState.networkStatus.estimated_total_loss_lpm.toFixed(1)} <span className="text-xs text-slate-400 font-sans">LPM</span>
            </div>
            <p className="text-[10px] text-slate-400 mt-1">
              Model-derived simulation estimate
            </p>
          </div>
        </div>

        {/* MAIN MIDDLE SECTION: NETWORK TOPOLOGY MAP & INCIDENT SIDEBAR */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left 2 Columns: Live Network Topology Map (Centerpiece Visualization) */}
          <div className="lg:col-span-2 space-y-4">
            <NetworkTopologyMap
              topology={CANONICAL_TOPOLOGY}
              highlightedSegment={activeState.highlightedSegment}
              faultySensors={activeState.faultySensors}
              activeIncident={activeIncident}
              onSelectSegment={(id) => setSelectedSegment(id)}
              onSelectSensor={(id) => setSelectedSensor(id)}
            />
          </div>

          {/* Right 1 Column: Active Incident Panel & Inspector */}
          <div className="space-y-4">
            {/* Active Incident Quick Card */}
            {activeIncident ? (
              <div className="bg-[#0f172a] border border-rose-500/40 rounded-xl p-5 shadow-xl space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5 text-rose-500 animate-pulse" />
                    <div>
                      <h3 className="font-bold text-white text-base">{activeIncident.incident_type}</h3>
                      <span className="text-xs text-slate-400 font-mono">ID: {activeIncident.incident_id}</span>
                    </div>
                  </div>
                  <span className={`px-2.5 py-0.5 rounded text-xs font-bold font-mono ${
                    activeIncident.status === "OPEN" ? "bg-rose-500/20 text-rose-300 border border-rose-500/40" :
                    activeIncident.status === "ACKNOWLEDGED" ? "bg-amber-500/20 text-amber-300 border border-amber-500/40" :
                    "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                  }`}>
                    {activeIncident.status}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div className="bg-[#0b0f19] p-2.5 rounded border border-slate-800">
                    <span className="text-slate-400 block mb-0.5">Affected Segment</span>
                    <span className="font-bold text-rose-400 font-mono text-sm">{activeIncident.affected_segment}</span>
                  </div>
                  <div className="bg-[#0b0f19] p-2.5 rounded border border-slate-800">
                    <span className="text-slate-400 block mb-0.5">Confidence Score</span>
                    <span className="font-bold text-cyan-400 font-mono text-sm">{(activeIncident.confidence * 100).toFixed(1)}%</span>
                  </div>
                  <div className="bg-[#0b0f19] p-2.5 rounded border border-slate-800">
                    <span className="text-slate-400 block mb-0.5">Est. Flow Loss</span>
                    <span className="font-bold text-white font-mono text-sm">{activeIncident.estimated_flow_loss_lpm} LPM</span>
                  </div>
                  <div className="bg-[#0b0f19] p-2.5 rounded border border-slate-800">
                    <span className="text-slate-400 block mb-0.5">Est. Volume Loss</span>
                    <span className="font-bold text-white font-mono text-sm">{activeIncident.estimated_volume_loss_liters} L</span>
                  </div>
                </div>

                {/* Evidence Snippet */}
                <div className="bg-[#0b0f19] p-3 rounded border border-slate-800">
                  <span className="text-xs font-bold text-slate-300 block mb-1">Topology Evidence</span>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    {activeIncident.evidence[0] || "Correlated pressure drop detected across responsive sensors."}
                  </p>
                </div>

                {/* Operator Actions Buttons */}
                <div className="flex items-center gap-2 pt-2">
                  {activeIncident.status === "OPEN" && (
                    <button
                      onClick={() => acknowledgeIncident(activeIncident.incident_id)}
                      className="flex-1 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold py-2 rounded text-xs transition"
                    >
                      ACKNOWLEDGE
                    </button>
                  )}
                  {activeIncident.status !== "RESOLVED" && (
                    <button
                      onClick={() => resolveIncident(activeIncident.incident_id)}
                      className="flex-1 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold py-2 rounded text-xs transition"
                    >
                      RESOLVE
                    </button>
                  )}
                  <Link
                    href={`/incidents/${activeIncident.incident_id}`}
                    className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-xs border border-slate-700 transition"
                    title="View Full Investigation Page"
                  >
                    <ChevronRight className="w-4 h-4" />
                  </Link>
                </div>
              </div>
            ) : scenario === "sensor_fault" ? (
              /* Sensor Fault Quick Info Card */
              <div className="bg-[#0f172a] border border-amber-500/40 rounded-xl p-5 shadow-xl space-y-4">
                <div className="flex items-center gap-2 text-amber-400 pb-3 border-b border-slate-800">
                  <ShieldCheck className="w-5 h-5" />
                  <div>
                    <h3 className="font-bold text-white text-base">False Alarm Prevented</h3>
                    <span className="text-xs text-slate-400">Sensor B3 Telemetry Spike</span>
                  </div>
                </div>

                <div className="bg-[#0b0f19] p-3.5 rounded border border-slate-800 space-y-2 text-xs">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Sensor B3 (Target):</span>
                    <span className="text-amber-400 font-mono font-bold">5.85 bar (Spike)</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Neighbor B2 (Upstream):</span>
                    <span className="text-emerald-400 font-mono font-bold">3.00 bar (Normal)</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Neighbor B4 (Downstream):</span>
                    <span className="text-emerald-400 font-mono font-bold">3.00 bar (Normal)</span>
                  </div>
                </div>

                <p className="text-xs text-slate-300 leading-relaxed bg-amber-500/5 p-3 rounded border border-amber-500/20">
                  Anomaly is isolated to sensor telemetry electronics. No spatial pressure propagation detected across pipeline network topology. Pipeline B2-B3 remains completely healthy.
                </p>
              </div>
            ) : (
              /* Healthy Network Summary Card */
              <div className="bg-[#0f172a] border border-slate-800 rounded-xl p-5 shadow-md space-y-3">
                <div className="flex items-center gap-2 text-emerald-400">
                  <CheckCircle2 className="w-5 h-5" />
                  <h3 className="font-bold text-white text-base">Network Fully Operational</h3>
                </div>
                <p className="text-xs text-slate-400 leading-relaxed">
                  All 10 canonical sensors report normal operating pressures (3.0–3.5 bar) and baseline diurnal demand curves.
                </p>
                <div className="p-3 bg-[#0b0f19] rounded border border-slate-800 text-xs space-y-1">
                  <div className="flex justify-between text-slate-300">
                    <span>Active Pipeline Leaks:</span>
                    <span className="font-bold text-emerald-400">0</span>
                  </div>
                  <div className="flex justify-between text-slate-300">
                    <span>Estimated Total Loss:</span>
                    <span className="font-bold text-white">0.0 LPM</span>
                  </div>
                </div>
              </div>
            )}

            {/* Network Health Summary Card */}
            <div className="bg-[#0f172a] border border-slate-800 rounded-xl p-4 shadow-md space-y-3">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center justify-between">
                <span>Observability Intelligence</span>
                <Eye className="w-4 h-4 text-cyan-400" />
              </h4>

              <div className="space-y-2 text-xs">
                <div className="flex justify-between p-2 bg-[#0b0f19] rounded border border-slate-800">
                  <span className="text-slate-400">Strongest Segment:</span>
                  <span className="font-bold text-emerald-400 font-mono">B2-B3 (91.0%)</span>
                </div>
                <div className="flex justify-between p-2 bg-[#0b0f19] rounded border border-slate-800">
                  <span className="text-slate-400">Weakest Segment:</span>
                  <span className="font-bold text-rose-400 font-mono">C2-C3 (42.0%)</span>
                </div>
                <div className="flex justify-between p-2 bg-[#0b0f19] rounded border border-slate-800">
                  <span className="text-slate-400">Monitoring Blind Spots:</span>
                  <span className="font-bold text-amber-400 font-mono">1 Segment</span>
                </div>
              </div>

              <Link
                href="/network"
                className="w-full inline-flex items-center justify-center gap-1.5 text-xs text-cyan-400 hover:text-cyan-300 bg-cyan-500/10 hover:bg-cyan-500/20 py-2 rounded font-semibold transition"
              >
                <span>View Full Topology Intelligence</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        </div>

        {/* BOTTOM SECTION: AI INCIDENT ANALYSIS PANEL */}
        <AIAnalysisPanel
          whyDetected={activeState.aiAnalysis.whyDetected}
          recommendedActions={activeState.aiAnalysis.recommendedActions}
          confidenceNote={activeState.aiAnalysis.confidenceNote}
          limitations={activeState.aiAnalysis.limitations}
          isSensorFault={scenario === "sensor_fault"}
        />
      </div>
    </AppShell>
  );
}
