"use client";

import React from "react";
import { BellOff, Siren } from "lucide-react";
import { Incident } from "@/types";

interface AlarmBannerProps {
  incidents: Incident[];
  onStop: () => void;
}

export const AlarmBanner: React.FC<AlarmBannerProps> = ({ incidents, onStop }) => {
  const label = incidents.length === 1
    ? `${incidents[0].incident_type.replace("_", " ")} — ${incidents[0].affected_segment}`
    : `${incidents.length} CRITICAL INCIDENTS ACTIVE`;

  return (
    <div
      role="alert"
      aria-live="assertive"
      className="relative flex items-center justify-between px-5 py-2.5 bg-red-950 border-b border-red-700 z-50 overflow-hidden"
      style={{ animation: "alarmPulse 1s ease-in-out infinite" }}
    >
      {/* Animated background sweep */}
      <span
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 opacity-20"
        style={{
          background:
            "repeating-linear-gradient(90deg, #dc2626 0px, #dc2626 8px, transparent 8px, transparent 20px)",
          animation: "alarmStripe 0.6s linear infinite",
        }}
      />

      <div className="relative flex items-center gap-3">
        {/* Pulsing siren icon */}
        <span
          className="flex items-center justify-center w-8 h-8 rounded-full bg-red-600 shadow-[0_0_12px_rgba(220,38,38,0.8)]"
          style={{ animation: "alarmIconPulse 0.7s ease-in-out infinite" }}
        >
          <Siren className="w-4 h-4 text-white" />
        </span>

        <div>
          <p className="text-xs font-black tracking-widest text-red-200 uppercase leading-none">
            🚨 CRITICAL ALERT
          </p>
          <p className="text-[11px] text-red-300 font-mono mt-0.5 leading-none truncate max-w-xs">
            {label}
          </p>
        </div>
      </div>

      <button
        id="alarm-stop-btn"
        onClick={onStop}
        className="relative flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold bg-red-700 hover:bg-red-600 active:bg-red-800 text-white rounded border border-red-500 transition-colors shadow-md"
      >
        <BellOff className="w-3.5 h-3.5" />
        STOP ALARM
      </button>

      {/* Keyframe styles injected inline so they work without a global CSS change */}
      <style>{`
        @keyframes alarmPulse {
          0%, 100% { background-color: #450a0a; }
          50%       { background-color: #7f1d1d; }
        }
        @keyframes alarmStripe {
          from { background-position-x: 0; }
          to   { background-position-x: 28px; }
        }
        @keyframes alarmIconPulse {
          0%, 100% { transform: scale(1); opacity: 1; }
          50%       { transform: scale(1.15); opacity: 0.85; }
        }
      `}</style>
    </div>
  );
};
