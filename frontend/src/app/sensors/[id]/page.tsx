"use client";

import React, { use } from "react";
import Link from "next/link";
import { AppShell } from "@/components/layout/AppShell";
import { CANONICAL_TOPOLOGY } from "@/lib/demo/demoData";
import { useDemo } from "@/context/DemoContext";
import { Radio, ArrowLeft, Activity, ShieldCheck, Zap } from "lucide-react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine
} from "recharts";

export default function SensorDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { activeState } = useDemo();

  const sensor = CANONICAL_TOPOLOGY.sensors.find((s) => s.sensor_id === id) || CANONICAL_TOPOLOGY.sensors[5];
  const isFaulty = activeState.faultySensors.includes(sensor.sensor_id);

  // Generate 24-point diurnal telemetry trend data
  const trendData = Array.from({ length: 24 }).map((_, i) => {
    const hour = `${i < 10 ? "0" : ""}${i}:00`;
    let pressure = 3.0 + Math.sin(i / 3) * 0.3;
    let flow = 200 + Math.cos(i / 3) * 40;

    if (isFaulty && i >= 18) {
      pressure = 5.85; // Spike fault
      flow = 0.0;
    } else if (sensor.sensor_id === "B3" && activeState.highlightedSegment === "B2-B3" && i >= 15) {
      pressure = 2.30; // Leak drop
      flow = 209.1;
    }

    return {
      time: hour,
      pressure: Number(pressure.toFixed(2)),
      flow: Number(flow.toFixed(1)),
      baselinePressure: 3.0
    };
  });

  return (
    <AppShell>
      <div className="p-6 max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center gap-4">
            <Link
              href="/sensors"
              className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg border border-slate-700 transition"
            >
              <ArrowLeft className="w-4 h-4" />
            </Link>
            <div>
              <div className="flex items-center gap-3">
                <h1 className="text-xl font-bold text-white tracking-tight">Sensor {sensor.sensor_id} Detail</h1>
                <span className="text-xs font-mono text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/30">
                  {sensor.sensor_type}
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-1">
                Deployed at node {sensor.location_node} ({sensor.zone_id} / Segment {sensor.pipeline_segment_id})
              </p>
            </div>
          </div>

          <span
            className={`px-3 py-1 rounded text-xs font-bold font-mono ${
              isFaulty
                ? "bg-amber-500/20 text-amber-300 border border-amber-500/40 animate-pulse"
                : "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
            }`}
          >
            {isFaulty ? "STATUS: FAULTY" : "STATUS: HEALTHY"}
          </span>
        </div>

        {/* Telemetry Charts (Recharts) */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Pressure Trend Line Chart */}
          <div className="bg-[#0f172a] border border-slate-800 rounded-xl p-5 shadow-md space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                <Activity className="w-4 h-4 text-cyan-400" />
                24-Hour Pressure Telemetry (Bar)
              </h3>
              <span className="text-xs font-mono text-cyan-400">Baseline: 3.0 Bar</span>
            </div>

            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={trendData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="time" stroke="#64748b" fontSize={11} />
                  <YAxis stroke="#64748b" fontSize={11} domain={[1.0, 7.0]} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", color: "#f8fafc" }}
                  />
                  <ReferenceLine y={3.0} stroke="#06b6d4" strokeDasharray="3 3" />
                  <Line type="monotone" dataKey="pressure" stroke={isFaulty ? "#f59e0b" : "#38bdf8"} strokeWidth={2.5} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Flow Rate Trend Line Chart */}
          <div className="bg-[#0f172a] border border-slate-800 rounded-xl p-5 shadow-md space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                <Radio className="w-4 h-4 text-emerald-400" />
                24-Hour Flow Rate Telemetry (LPM)
              </h3>
              <span className="text-xs font-mono text-emerald-400">Baseline: 200 LPM</span>
            </div>

            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={trendData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="time" stroke="#64748b" fontSize={11} />
                  <YAxis stroke="#64748b" fontSize={11} domain={[0, 350]} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", color: "#f8fafc" }}
                  />
                  <ReferenceLine y={200} stroke="#10b981" strokeDasharray="3 3" />
                  <Line type="monotone" dataKey="flow" stroke="#10b981" strokeWidth={2.5} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
