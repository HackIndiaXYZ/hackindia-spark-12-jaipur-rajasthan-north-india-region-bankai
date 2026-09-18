"use client";

import React from "react";
import { BellOff, Siren, Volume2, Cpu, Activity } from "lucide-react";
import { Incident } from "@/types";

interface AlarmBannerProps {
  isHardwareAlert: boolean;
  raw_value?: number;
  threshold?: number;
  pressure_equivalent?: number;
  incidents: Incident[];
  isAudioUnlocked: boolean;
  onUnlockAudio: () => void;
  onStop: () => void;
}

export const AlarmBanner: React.FC<AlarmBannerProps> = ({
  isHardwareAlert,
  raw_value = 0,
  threshold = 50,
  pressure_equivalent = 0,
  incidents,
  isAudioUnlocked,
  onUnlockAudio,
  onStop,
}) => {
  const incidentLabel =
    incidents.length === 1
      ? `${incidents[0].incident_type.replace("_", " ")} — Segment ${incidents[0].affected_segment}`
      : `${incidents.length} CRITICAL SIMULATION INCIDENTS ACTIVE`;

  return (
    <div
      role="alert"
      aria-live="assertive"
      className="relative flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 px-5 py-3 bg-rose-950/90 border-b border-rose-600 z-50 overflow-hidden shadow-2xl backdrop-blur-md"
      style={{ animation: "alarmPulse 1s ease-in-out infinite" }}
    >
      {/* Background Warning Stripes */}
      <span
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 opacity-15"
        style={{
          background:
            "repeating-linear-gradient(90deg, #e11d48 0px, #e11d48 10px, transparent 10px, transparent 24px)",
          animation: "alarmStripe 0.6s linear infinite",
        }}
      />

      {/* Main Alert Information */}
      <div className="relative flex items-center gap-3">
        <span
          className="flex items-center justify-center w-9 h-9 rounded-full bg-rose-600 text-white shadow-[0_0_15px_rgba(225,29,72,0.9)]"
          style={{ animation: "alarmIconPulse 0.7s ease-in-out infinite" }}
        >
          <Siren className="w-5 h-5 text-white" />
        </span>

        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-black tracking-wider text-rose-100 uppercase">
              🔴 {isHardwareAlert ? "PRESSURE-EQUIVALENT ALERT" : "CRITICAL PIPELINE ALARM"}
            </span>
            <span
              className={`text-[10px] px-2 py-0.5 rounded font-mono font-bold border ${
                isHardwareAlert
                  ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/40"
                  : "bg-amber-500/20 text-amber-300 border-amber-500/40"
              }`}
            >
              {isHardwareAlert ? "Source: LIVE HARDWARE (ESP32)" : "Source: SIMULATION ENGINE"}
            </span>
          </div>

          <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-rose-200 font-mono mt-1">
            <span className="flex items-center gap-1 font-semibold text-rose-300">
              <Volume2 className="w-3.5 h-3.5 text-rose-400 animate-pulse" />
              🔊 AUDIBLE ALARM ACTIVE
            </span>
            <span>•</span>
            <span className="font-semibold text-amber-300">
              Physical Buzzer: {isHardwareAlert ? "ON (GPIO32)" : "OFF"}
            </span>
            {isHardwareAlert && (
              <>
                <span>•</span>
                <span className="text-slate-300">
                  Raw ADC: <strong className="text-white">{raw_value}</strong> (Threshold: {threshold})
                </span>
                <span>•</span>
                <span className="text-cyan-300">
                  Simulated Pressure Eq: <strong className="text-white">{pressure_equivalent.toFixed(1)}%</strong>
                </span>
              </>
            )}
            {!isHardwareAlert && (
              <span className="text-rose-300">{incidentLabel}</span>
            )}
          </div>
        </div>
      </div>

      {/* Control Buttons */}
      <div className="relative flex items-center gap-2 self-end sm:self-center">
        {!isAudioUnlocked && (
          <button
            onClick={onUnlockAudio}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold bg-amber-500 hover:bg-amber-400 text-slate-950 rounded shadow-md transition"
          >
            <Volume2 className="w-3.5 h-3.5" />
            Enable Alarm Sound
          </button>
        )}

        <button
          id="alarm-stop-btn"
          onClick={onStop}
          className="flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-bold bg-rose-700 hover:bg-rose-600 active:bg-rose-800 text-white rounded border border-rose-500 transition-colors shadow-md"
        >
          <BellOff className="w-3.5 h-3.5" />
          MUTE LAPTOP ALARM
        </button>
      </div>

      {/* Inline Keyframes */}
      <style>{`
        @keyframes alarmPulse {
          0%, 100% { background-color: #4c0519; }
          50%       { background-color: #881337; }
        }
        @keyframes alarmStripe {
          from { background-position-x: 0; }
          to   { background-position-x: 34px; }
        }
        @keyframes alarmIconPulse {
          0%, 100% { transform: scale(1); opacity: 1; }
          50%       { transform: scale(1.15); opacity: 0.85; }
        }
      `}</style>
    </div>
  );
};
