"use client";

import React, { useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { NetworkTopologyMap } from "@/components/network/NetworkTopologyMap";
import { useDemo } from "@/context/DemoContext";
import { CANONICAL_TOPOLOGY } from "@/lib/demo/demoData";
import { Network, Eye, ShieldAlert, Radio, Activity, CheckCircle2 } from "lucide-react";

export default function NetworkPage() {
  const { activeState } = useDemo();
  const [selectedSegmentId, setSelectedSegmentId] = useState<string | null>("B2-B3");

  const selectedSegment = CANONICAL_TOPOLOGY.segments.find((s) => s.segment_id === selectedSegmentId) || CANONICAL_TOPOLOGY.segments[5];

  return (
    <AppShell>
      <div className="p-6 max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div>
            <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
              <Network className="w-5 h-5 text-cyan-400" />
              Network Observability & Blind-Spot Intelligence
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Topology graph analysis, segment observability indices, and virtual sensor placement recommendations
            </p>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-xs font-mono bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 px-3 py-1 rounded-full font-semibold">
              INDEX: 89.7% OBSERVABLE
            </span>
          </div>
        </div>

        {/* TOPOLOGY MAP & SEGMENT INSPECTION */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <NetworkTopologyMap
              topology={CANONICAL_TOPOLOGY}
              highlightedSegment={activeState.highlightedSegment}
              faultySensors={activeState.faultySensors}
              onSelectSegment={(id) => setSelectedSegmentId(id)}
            />
          </div>

          {/* Segment Inspector Drawer */}
          <div className="space-y-4">
            <div className="bg-[#0f172a] border border-slate-800 rounded-xl p-5 shadow-md space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <h3 className="font-bold text-white text-base">Segment Intelligence</h3>
                <span className="text-xs font-mono text-cyan-400 bg-cyan-950 px-2 py-0.5 rounded border border-cyan-800">
                  {selectedSegment.segment_id}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="bg-[#0b0f19] p-2.5 rounded border border-slate-800">
                  <span className="text-slate-400 block mb-0.5">Source Node</span>
                  <span className="font-bold text-white font-mono">{selectedSegment.source_node}</span>
                </div>
                <div className="bg-[#0b0f19] p-2.5 rounded border border-slate-800">
                  <span className="text-slate-400 block mb-0.5">Destination Node</span>
                  <span className="font-bold text-white font-mono">{selectedSegment.destination_node}</span>
                </div>
                <div className="bg-[#0b0f19] p-2.5 rounded border border-slate-800">
                  <span className="text-slate-400 block mb-0.5">Length (Meters)</span>
                  <span className="font-bold text-white font-mono">{selectedSegment.length_m} m</span>
                </div>
                <div className="bg-[#0b0f19] p-2.5 rounded border border-slate-800">
                  <span className="text-slate-400 block mb-0.5">Zone</span>
                  <span className="font-bold text-cyan-400 font-mono">{selectedSegment.zone_id}</span>
                </div>
              </div>

              <div className="space-y-2 text-xs">
                <span className="text-slate-400 font-semibold block">Nominal Operating Ranges:</span>
                <div className="flex justify-between p-2 bg-[#0b0f19] rounded border border-slate-800 text-slate-300">
                  <span>Pressure Range:</span>
                  <span className="font-mono text-white font-bold">{selectedSegment.nominal_min_pressure} – {selectedSegment.nominal_max_pressure} bar</span>
                </div>
                <div className="flex justify-between p-2 bg-[#0b0f19] rounded border border-slate-800 text-slate-300">
                  <span>Flow Rate Range:</span>
                  <span className="font-mono text-white font-bold">{selectedSegment.nominal_min_flow} – {selectedSegment.nominal_max_flow} LPM</span>
                </div>
              </div>
            </div>

            {/* Virtual Sensor Candidate Engine Card */}
            <div className="bg-[#0f172a] border border-cyan-500/30 rounded-xl p-5 shadow-md space-y-3">
              <div className="flex items-center gap-2 text-cyan-400">
                <Eye className="w-5 h-5" />
                <h3 className="font-bold text-white text-sm">Virtual Sensor Candidate Engine</h3>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Evaluates candidate virtual sensor placements to eliminate monitoring blind spots in Zone C industrial trunk.
              </p>
              <div className="p-3 bg-[#0b0f19] rounded border border-slate-800 text-xs space-y-1">
                <div className="flex justify-between text-slate-300">
                  <span>Candidate Placement:</span>
                  <span className="font-bold text-cyan-400 font-mono">Node C2 (Segment C1-C2)</span>
                </div>
                <div className="flex justify-between text-slate-300">
                  <span>Observability Improvement:</span>
                  <span className="font-bold text-emerald-400 font-mono">+18.5% (42% → 60.5%)</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
