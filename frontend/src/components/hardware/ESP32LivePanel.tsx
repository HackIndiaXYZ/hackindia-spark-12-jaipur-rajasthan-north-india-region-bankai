"use client";

import React, { useEffect, useState } from "react";
import { Cpu, AlertTriangle, CheckCircle, WifiOff, Activity, Gauge, Zap } from "lucide-react";
import { getApiEndpoint } from "@/lib/api/client";

interface TelemetryPayload {
  device_id: string;
  sensor_id: string;
  zone_id: string;
  raw_value: number;
  pressure_equivalent: number;
  threshold: number;
  status: string;
  timestamp_ms: number;
}


interface HardwareState {
  connection_state: "LIVE HARDWARE" | "DISCONNECTED" | "SIMULATION";
  last_received_at: string | null;
  telemetry: TelemetryPayload | null;
  derived_flow_lpm: number | null;
  pipeline_incident: Record<string, any> | null;
}

export const ESP32LivePanel: React.FC = () => {
  const [hardwareState, setHardwareState] = useState<HardwareState>({
    connection_state: "SIMULATION",
    last_received_at: null,
    telemetry: null,
    derived_flow_lpm: null,
    pipeline_incident: null,
  });

  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchHardwareStatus = async () => {
      try {
        const res = await fetch(getApiEndpoint("/hardware/latest"), { cache: "no-store" });
        if (res.ok) {
          const data = await res.json();
          setHardwareState(data);
        }
      } catch (err) {
        // Backend offline or unreachable
        setHardwareState((prev) => ({
          ...prev,
          connection_state: "DISCONNECTED",
        }));
      } finally {
        setIsLoading(false);
      }
    };

    fetchHardwareStatus();
    const interval = setInterval(fetchHardwareStatus, 500); // 500ms polling for live hardware reactivity
    return () => clearInterval(interval);
  }, []);

  const isLive = hardwareState.connection_state === "LIVE HARDWARE";
  const isDisconnected = hardwareState.connection_state === "DISCONNECTED";
  const telemetry = hardwareState.telemetry;
  const isAlert = telemetry?.status === "ALERT";

  return (
    <div
      className={`rounded-xl border p-5 transition-all duration-300 shadow-xl relative overflow-hidden ${
        isAlert
          ? "bg-gradient-to-r from-[#1e1b4b] via-[#0f172a] to-[#31101e] border-rose-500/80 shadow-[0_0_25px_rgba(244,63,94,0.3)] animate-pulse"
          : isLive
          ? "bg-[#0f172a] border-cyan-500/40 shadow-[0_0_15px_rgba(6,182,212,0.15)]"
          : "bg-[#0f172a] border-slate-800"
      }`}
    >
      {/* Background Tech Mesh Glow */}
      <div className="absolute top-0 right-0 w-64 h-64 bg-cyan-500/5 rounded-full blur-3xl pointer-events-none" />

      {/* Header Row */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-4 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div
            className={`p-2.5 rounded-lg border ${
              isAlert
                ? "bg-rose-500/20 text-rose-400 border-rose-500/40"
                : isLive
                ? "bg-cyan-500/20 text-cyan-400 border-cyan-500/40"
                : "bg-slate-800 text-slate-400 border-slate-700"
            }`}
          >
            <Cpu className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-bold text-white tracking-tight">
                Physical ESP32 Prototype Telemetry
              </h2>
              <span className="text-[10px] bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 px-2 py-0.5 rounded font-mono">
                USB SERIAL
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              FSR402 force-input simulator mapped to node B2 (Zone_B) • Local GPIO32 Buzzer
            </p>
          </div>
        </div>

        {/* Status Badges */}
        <div className="flex items-center gap-2">
          {/* Connection State Badge */}
          <span
            className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold font-mono tracking-wide ${
              isLive
                ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/50 shadow-[0_0_10px_rgba(16,185,129,0.3)]"
                : isDisconnected
                ? "bg-rose-500/20 text-rose-400 border border-rose-500/50"
                : "bg-amber-500/20 text-amber-300 border border-amber-500/50"
            }`}
          >
            <span
              className={`w-2 h-2 rounded-full ${
                isLive ? "bg-emerald-400 animate-ping" : isDisconnected ? "bg-rose-400" : "bg-amber-400"
              }`}
            />
            {hardwareState.connection_state}
          </span>

          {/* ESP32 Status Badge */}
          {telemetry && (
            <span
              className={`px-3 py-1 rounded-full text-xs font-bold font-mono ${
                isAlert
                  ? "bg-rose-600 text-white animate-bounce shadow-md"
                  : "bg-emerald-950 text-emerald-300 border border-emerald-700"
              }`}
            >
              {telemetry.status}
            </span>
          )}
        </div>
      </div>

      {/* Main Content Grid */}
      {isLive && telemetry ? (
        <div className="mt-4 grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3 text-xs">
          {/* FSR Raw ADC Reading */}
          <div className="bg-[#0b0f19] p-3 rounded-lg border border-slate-800">
            <span className="text-slate-400 block text-[11px] mb-1">Raw ADC Value</span>
            <div className="flex items-baseline gap-1">
              <span className="text-xl font-bold font-mono text-white">{telemetry.raw_value}</span>
              <span className="text-[10px] text-slate-500 font-mono">/ 4095</span>
            </div>
            <span className="text-[10px] text-slate-500 block mt-1">GPIO34 Analog</span>
          </div>

          {/* Pressure-Equivalent */}
          <div className="bg-[#0b0f19] p-3 rounded-lg border border-slate-800">
            <span className="text-slate-400 block text-[11px] mb-1">Simulated Pressure</span>
            <div className="flex items-baseline gap-1">
              <span
                className={`text-xl font-bold font-mono ${
                  isAlert ? "text-rose-400" : "text-cyan-400"
                }`}
              >
                {telemetry.pressure_equivalent.toFixed(1)}
              </span>
              <span className="text-[10px] text-slate-400">eq %</span>
            </div>
            <span className="text-[10px] text-slate-500 block mt-1">Prototype scale</span>
          </div>

          {/* Hardware Alert Threshold */}
          <div className="bg-[#0b0f19] p-3 rounded-lg border border-slate-800">
            <span className="text-slate-400 block text-[11px] mb-1">Alert Threshold</span>
            <div className="flex items-baseline gap-1">
              <span className="text-xl font-bold font-mono text-amber-400">{telemetry.threshold}</span>
              <span className="text-[10px] text-slate-500">raw ADC</span>
            </div>
            <span className="text-[10px] text-slate-500 block mt-1">ESP32 Firmware</span>
          </div>

          {/* Derived Flow (Compatibility Mechanism) */}
          <div className="bg-[#0b0f19] p-3 rounded-lg border border-slate-800">
            <span className="text-slate-400 block text-[11px] mb-1">Derived Flow</span>
            <div className="flex items-baseline gap-1">
              <span className="text-xl font-bold font-mono text-white">
                {hardwareState.derived_flow_lpm?.toFixed(1) ?? "120.0"}
              </span>
              <span className="text-[10px] text-slate-400">LPM</span>
            </div>
            <span className="text-[10px] text-indigo-400 block mt-1">Pipeline compatibility</span>
          </div>

          {/* Sensor Mapping */}
          <div className="bg-[#0b0f19] p-3 rounded-lg border border-slate-800">
            <span className="text-slate-400 block text-[11px] mb-1">Target Mapping</span>
            <div className="text-sm font-bold font-mono text-slate-200">{telemetry.sensor_id} ({telemetry.zone_id})</div>
            <span className="text-[10px] text-slate-500 block mt-1">Segment B2-B3</span>
          </div>

          {/* Local Buzzer Hardware Status */}
          <div className="bg-[#0b0f19] p-3 rounded-lg border border-slate-800">
            <span className="text-slate-400 block text-[11px] mb-1">Physical Buzzer</span>
            <div className="flex items-center gap-1.5 mt-0.5">
              <Zap className={`w-4 h-4 ${isAlert ? "text-rose-400 animate-pulse" : "text-slate-600"}`} />
              <span className={`font-bold font-mono text-xs ${isAlert ? "text-rose-400" : "text-slate-400"}`}>
                {isAlert ? "GPIO32 ON" : "GPIO32 OFF"}
              </span>
            </div>
            <span className="text-[10px] text-slate-500 block mt-1">Standalone logic</span>
          </div>
        </div>
      ) : (
        /* Disconnected / Simulation Fallback Banner */
        <div className="mt-4 p-4 rounded-lg bg-[#0b0f19] border border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <WifiOff className="w-5 h-5 text-amber-400" />
            <div>
              <p className="text-xs font-semibold text-slate-200">
                {isDisconnected
                  ? "ESP32 Hardware Disconnected — Running on Simulation Pipeline"
                  : "Simulation Fallback Mode Active"}
              </p>
              <p className="text-[11px] text-slate-400">
                Connect ESP32 via USB and start <code className="text-cyan-400">python esp32_bridge.py</code> to stream live force sensor telemetry.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Force Pressure Level Indicator Bar */}
      {isLive && telemetry && (
        <div className="mt-4 space-y-1">
          <div className="flex justify-between items-center text-[10px] text-slate-400">
            <span>FSR Force Pressure Level</span>
            <span className="font-mono text-slate-300">
              {Math.min(100, Math.round((telemetry.raw_value / 4095) * 100 * 10)) / 10}% Applied Force
            </span>
          </div>
          <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
            <div
              className={`h-full transition-all duration-300 ${
                isAlert ? "bg-gradient-to-r from-amber-500 to-rose-500" : "bg-gradient-to-r from-cyan-500 to-emerald-500"
              }`}
              style={{ width: `${Math.min(100, Math.max(5, (telemetry.raw_value / 500) * 100))}%` }}
            />
          </div>
        </div>
      )}

      {/* Hardware Clarification Footer */}
      <div className="mt-3 pt-2 border-t border-slate-800/60 flex flex-wrap items-center justify-between text-[10px] text-slate-500">
        <span>* FSR402 is a prototype force-input simulator. Values represent relative force scale, not calibrated hydraulic PSI.</span>
        <span>Bridge API: <code className="text-slate-400">/api/hardware/latest</code></span>
      </div>
    </div>
  );
};
