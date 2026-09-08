"use client";

import React from "react";
import Link from "next/link";
import { AppShell } from "@/components/layout/AppShell";
import { CANONICAL_TOPOLOGY } from "@/lib/demo/demoData";
import { useDemo } from "@/context/DemoContext";
import { Radio, ChevronRight, Activity, ShieldCheck, AlertTriangle } from "lucide-react";

export default function SensorsListPage() {
  const { activeState } = useDemo();

  return (
    <AppShell>
      <div className="p-6 max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div>
            <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
              <Radio className="w-5 h-5 text-cyan-400" />
              Telemetry Sensors Directory (10 Canonical Nodes)
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Active telemetry pressure and flow sensors deployed across Zone A, Zone B, and Zone C
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 px-3 py-1 rounded-full font-semibold">
              {10 - activeState.faultySensors.length} / 10 HEALTHY
            </span>
          </div>
        </div>

        {/* Sensors Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {CANONICAL_TOPOLOGY.sensors.map((sensor) => {
            const isFaulty = activeState.faultySensors.includes(sensor.sensor_id);
            const isAnomalous = activeState.activeAnomalies.some((a) => a.sensor_id === sensor.sensor_id);

            return (
              <div
                key={sensor.sensor_id}
                className="bg-[#0f172a] border border-slate-800 hover:border-cyan-500/40 rounded-xl p-5 shadow-md transition space-y-4"
              >
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <div className="flex items-center gap-2.5">
                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center font-bold text-xs font-mono border ${
                      isFaulty ? "bg-amber-500/20 text-amber-300 border-amber-500/40" : "bg-cyan-500/20 text-cyan-300 border-cyan-500/40"
                    }`}>
                      {sensor.sensor_id}
                    </div>
                    <div>
                      <h3 className="font-bold text-white text-sm">Sensor {sensor.sensor_id}</h3>
                      <span className="text-[11px] text-slate-400">{sensor.zone_id} ({sensor.pipeline_segment_id})</span>
                    </div>
                  </div>

                  <span className={`px-2.5 py-0.5 rounded text-[11px] font-bold font-mono ${
                    isFaulty
                      ? "bg-amber-500/20 text-amber-300 border border-amber-500/40 animate-pulse"
                      : isAnomalous
                      ? "bg-rose-500/20 text-rose-300 border border-rose-500/40"
                      : "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                  }`}>
                    {isFaulty ? "FAULTY" : isAnomalous ? "ANOMALOUS" : "HEALTHY"}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="bg-[#0b0f19] p-2 rounded border border-slate-800">
                    <span className="text-slate-400 block mb-0.5">Pressure</span>
                    <span className="font-bold text-white font-mono">
                      {isFaulty ? "5.85 bar (Spike)" : isAnomalous ? "2.30 bar (Drop)" : "3.00 bar"}
                    </span>
                  </div>
                  <div className="bg-[#0b0f19] p-2 rounded border border-slate-800">
                    <span className="text-slate-400 block mb-0.5">Flow Rate</span>
                    <span className="font-bold text-white font-mono">
                      {isFaulty ? "0.0 LPM" : isAnomalous ? "209.1 LPM" : "200.0 LPM"}
                    </span>
                  </div>
                </div>

                <Link
                  href={`/sensors/${sensor.sensor_id}`}
                  className="w-full inline-flex items-center justify-between text-xs text-slate-300 hover:text-cyan-400 bg-slate-800/80 hover:bg-slate-800 px-3 py-2 rounded border border-slate-700 transition font-medium"
                >
                  <span>View Telemetry Trends & Z-Scores</span>
                  <ChevronRight className="w-4 h-4 text-cyan-400" />
                </Link>
              </div>
            );
          })}
        </div>
      </div>
    </AppShell>
  );
}
