"use client";

import React, { useState } from "react";
import { NetworkTopology, Incident } from "@/types";
import { Droplets } from "lucide-react";

interface NetworkTopologyMapProps {
  topology: NetworkTopology;
  highlightedSegment: string | null;
  faultySensors: string[];
  activeIncident?: Incident | null;
  onSelectSegment?: (segmentId: string) => void;
  onSelectSensor?: (sensorId: string) => void;
}

// Fixed 2D node coordinates for optimal control-room visualization
const NODE_COORDINATES: Record<string, { x: number; y: number; label: string; zone: string }> = {
  R0: { x: 450, y: 55, label: "Reservoir R0", zone: "Source" },
  // Zone A (Left Branch)
  A1: { x: 180, y: 150, label: "A1 (Pressure Node)", zone: "Zone_A" },
  A2: { x: 130, y: 270, label: "A2 (Sub-station)", zone: "Zone_A" },
  A3: { x: 90, y: 390, label: "A3 (Consumer End)", zone: "Zone_A" },
  // Zone B (Center Trunk)
  B1: { x: 450, y: 160, label: "B1 (Header Node)", zone: "Zone_B" },
  B2: { x: 450, y: 280, label: "B2 (Distribution)", zone: "Zone_B" },
  B3: { x: 450, y: 400, label: "B3 (Mid-Trunk)", zone: "Zone_B" },
  B4: { x: 450, y: 510, label: "B4 (Terminal)", zone: "Zone_B" },
  // Zone C (Right Branch)
  C1: { x: 720, y: 150, label: "C1 (Industrial In)", zone: "Zone_C" },
  C2: { x: 770, y: 270, label: "C2 (Plant Feed)", zone: "Zone_C" },
  C3: { x: 810, y: 390, label: "C3 (Industrial End)", zone: "Zone_C" }
};

export const NetworkTopologyMap: React.FC<NetworkTopologyMapProps> = ({
  topology,
  highlightedSegment,
  faultySensors,
  activeIncident,
  onSelectSegment,
  onSelectSensor
}) => {
  const [hoveredElement, setHoveredElement] = useState<{ type: "node" | "segment"; id: string } | null>(null);

  return (
    <div className="relative w-full bg-[#0f172a]/90 border border-slate-800 rounded-xl p-4 shadow-xl overflow-hidden">
      {/* Topology Header Info */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <Droplets className="w-5 h-5 text-cyan-400" />
          <h3 className="text-sm font-semibold text-white">AquaSentinel Topology Map (10 Sensors / 10 Segments)</h3>
        </div>

        {/* Legend */}
        <div className="flex items-center gap-4 text-xs font-medium text-slate-300 bg-[#0b0f19] px-3 py-1.5 rounded-lg border border-slate-800">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400"></span> Normal Node
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-400"></span> Sensor Node
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-400 animate-pulse"></span> Sensor Fault
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-1 bg-rose-500 animate-pulse"></span> Leak Segment
          </div>
        </div>
      </div>

      {/* Interactive SVG Network Map */}
      <div className="relative w-full h-[540px] bg-[#0b0f19] rounded-lg border border-slate-800/80 flex items-center justify-center">
        <svg viewBox="0 0 900 580" className="w-full h-full">
          <defs>
            {/* Background Grid Pattern */}
            <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(30, 41, 59, 0.4)" strokeWidth="1" />
            </pattern>
            {/* Glow Filter */}
            <filter id="glow-cyan" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="4" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
            <filter id="glow-red" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="6" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>

          {/* Grid Background */}
          <rect width="100%" height="100%" fill="url(#grid)" />

          {/* Zone Region Enclosures */}
          <g opacity="0.15">
            <path d="M 60,110 L 260,110 L 160,460 L 40,460 Z" fill="#3b82f6" />
            <path d="M 380,110 L 520,110 L 520,550 L 380,550 Z" fill="#06b6d4" />
            <path d="M 640,110 L 840,110 L 860,460 L 740,460 Z" fill="#8b5cf6" />
          </g>

          {/* Zone Labels */}
          <text x="120" y="130" fill="#60a5fa" fontSize="11" fontWeight="bold" opacity="0.6">ZONE A (Commercial)</text>
          <text x="405" y="130" fill="#22d3ee" fontSize="11" fontWeight="bold" opacity="0.6">ZONE B (Residential)</text>
          <text x="710" y="130" fill="#c084fc" fontSize="11" fontWeight="bold" opacity="0.6">ZONE C (Industrial)</text>

          {/* PIPELINE SEGMENT EDGES */}
          {topology.segments.map((seg) => {
            const src = NODE_COORDINATES[seg.source_node];
            const dst = NODE_COORDINATES[seg.destination_node];
            if (!src || !dst) return null;

            const isHighlighted = highlightedSegment === seg.segment_id;
            const isHovered = hoveredElement?.type === "segment" && hoveredElement.id === seg.segment_id;

            return (
              <g key={seg.segment_id} className="cursor-pointer" onClick={() => onSelectSegment?.(seg.segment_id)}>
                {/* Background Shadow Edge */}
                <line
                  x1={src.x}
                  y1={src.y}
                  x2={dst.x}
                  y2={dst.y}
                  stroke="#0f172a"
                  strokeWidth="10"
                  strokeLinecap="round"
                />

                {/* Main Pipeline Segment Line */}
                <line
                  x1={src.x}
                  y1={src.y}
                  x2={dst.x}
                  y2={dst.y}
                  stroke={isHighlighted ? "#ef4444" : isHovered ? "#38bdf8" : "#334155"}
                  strokeWidth={isHighlighted ? 7 : isHovered ? 5 : 3.5}
                  strokeLinecap="round"
                  className={isHighlighted ? "animate-pipe-leak" : "transition-all duration-300"}
                  filter={isHighlighted ? "url(#glow-red)" : undefined}
                />

                {/* Flow Direction Indicator Markers */}
                {!isHighlighted && (
                  <circle
                    cx={(src.x + dst.x) / 2}
                    cy={(src.y + dst.y) / 2}
                    r="3"
                    fill={isHovered ? "#38bdf8" : "#475569"}
                  />
                )}

                {/* Segment ID Badge */}
                <g transform={`translate(${(src.x + dst.x) / 2}, ${(src.y + dst.y) / 2 - 12})`}>
                  <rect
                    x="-24"
                    y="-9"
                    width="48"
                    height="17"
                    rx="4"
                    fill={isHighlighted ? "#991b1b" : "#0f172a"}
                    stroke={isHighlighted ? "#ef4444" : "#334155"}
                    strokeWidth="1"
                  />
                  <text
                    x="0"
                    y="3"
                    textAnchor="middle"
                    fill={isHighlighted ? "#fecdd3" : "#94a3b8"}
                    fontSize="10"
                    fontWeight="bold"
                    fontFamily="monospace"
                  >
                    {seg.segment_id}
                  </text>
                </g>
              </g>
            );
          })}

          {/* NODES & SENSORS */}
          {topology.nodes.map((node) => {
            const pos = NODE_COORDINATES[node.node_id];
            if (!pos) return null;

            const sensor = topology.sensors.find((s) => s.location_node === node.node_id);
            const isFaulty = sensor ? faultySensors.includes(sensor.sensor_id) : false;
            const isReservoir = node.node_type === "RESERVOIR";
            const isResponsive = activeIncident?.responsive_sensors.includes(node.node_id);

            return (
              <g
                key={node.node_id}
                transform={`translate(${pos.x}, ${pos.y})`}
                className="cursor-pointer"
                onMouseEnter={() => setHoveredElement({ type: "node", id: node.node_id })}
                onMouseLeave={() => setHoveredElement(null)}
                onClick={() => sensor && onSelectSensor?.(sensor.sensor_id)}
              >
                {/* Responsive Sensor Highlight Ring */}
                {isResponsive && !isFaulty && (
                  <circle
                    r="24"
                    fill="none"
                    stroke="#06b6d4"
                    strokeWidth="2"
                    strokeDasharray="4 2"
                    className="animate-spin"
                    style={{ animationDuration: "8s" }}
                  />
                )}

                {/* Faulty Sensor Pulsing Ring */}
                {isFaulty && (
                  <circle
                    r="22"
                    fill="none"
                    stroke="#ef4444"
                    strokeWidth="3"
                    className="animate-sensor-fault"
                  />
                )}

                {/* Node Outer Circle */}
                <circle
                  r={isReservoir ? "22" : "15"}
                  fill={
                    isReservoir
                      ? "#1e3a8a"
                      : isFaulty
                      ? "#b45309"
                      : sensor
                      ? "#0f766e"
                      : "#1e293b"
                  }
                  stroke={
                    isReservoir
                      ? "#60a5fa"
                      : isFaulty
                      ? "#f59e0b"
                      : sensor
                      ? "#22d3ee"
                      : "#475569"
                  }
                  strokeWidth={isReservoir ? "3" : "2"}
                  filter={sensor && !isFaulty ? "url(#glow-cyan)" : undefined}
                />

                {/* Inner Icon or Label */}
                <text
                  textAnchor="middle"
                  dy="4"
                  fill="#ffffff"
                  fontSize={isReservoir ? "12" : "11"}
                  fontWeight="bold"
                  fontFamily="sans-serif"
                >
                  {node.node_id}
                </text>

                {/* Sensor ID Tag */}
                {sensor && (
                  <g transform="translate(0, 26)">
                    <rect
                      x="-20"
                      y="-8"
                      width="40"
                      height="16"
                      rx="3"
                      fill={isFaulty ? "#7f1d1d" : "#0f172a"}
                      stroke={isFaulty ? "#ef4444" : "#06b6d4"}
                      strokeWidth="1"
                    />
                    <text
                      x="0"
                      y="3"
                      textAnchor="middle"
                      fill={isFaulty ? "#fca5a5" : "#22d3ee"}
                      fontSize="9"
                      fontWeight="bold"
                    >
                      {isFaulty ? "FAULT" : sensor.sensor_id}
                    </text>
                  </g>
                )}
              </g>
            );
          })}

          {/* ACTIVE LEAK INCIDENT OVERLAY BADGE (Placed over B2-B3) */}
          {highlightedSegment === "B2-B3" && activeIncident && (
            <g transform="translate(450, 340)">
              <rect
                x="-110"
                y="-25"
                width="220"
                height="50"
                rx="8"
                fill="#881337"
                stroke="#f43f5e"
                strokeWidth="2"
                filter="url(#glow-red)"
              />
              <text x="0" y="-7" textAnchor="middle" fill="#ffe4e6" fontSize="12" fontWeight="bold">
                ⚠️ LEAK DETECTED (B2-B3)
              </text>
              <text x="0" y="12" textAnchor="middle" fill="#fecdd3" fontSize="10" fontWeight="medium">
                Conf: {(activeIncident.confidence * 100).toFixed(1)}% | Loss: {activeIncident.estimated_flow_loss_lpm} LPM
              </text>
            </g>
          )}

          {/* SENSOR FAULT OVERLAY BADGE (Placed near B3) */}
          {faultySensors.includes("B3") && highlightedSegment === null && (
            <g transform="translate(540, 400)">
              <rect
                x="-10"
                y="-25"
                width="220"
                height="50"
                rx="8"
                fill="#78350f"
                stroke="#f59e0b"
                strokeWidth="2"
              />
              <text x="100" y="-6" textAnchor="middle" fill="#fef3c7" fontSize="12" fontWeight="bold">
                ⚡ SENSOR FAULT DETECTED
              </text>
              <text x="100" y="12" textAnchor="middle" fill="#fde68a" fontSize="10" fontWeight="medium">
                Sensor B3 Erratic | Pipe Healthy
              </text>
            </g>
          )}
        </svg>
      </div>

      {/* Interactive Segment/Sensor Status Footer */}
      <div className="mt-3 grid grid-cols-3 gap-3 text-xs">
        <div className="bg-[#0b0f19] p-2.5 rounded-lg border border-slate-800">
          <span className="text-slate-400 block mb-0.5">Primary Affected Segment</span>
          <span className="font-bold text-white font-mono">
            {highlightedSegment || "None (Network Healthy)"}
          </span>
        </div>
        <div className="bg-[#0b0f19] p-2.5 rounded-lg border border-slate-800">
          <span className="text-slate-400 block mb-0.5">Sensor Telemetry Status</span>
          <span className={`font-bold font-mono ${faultySensors.length > 0 ? "text-amber-400" : "text-emerald-400"}`}>
            {faultySensors.length > 0 ? `Faulty Sensor: ${faultySensors.join(", ")}` : "All 10 Sensors Healthy"}
          </span>
        </div>
        <div className="bg-[#0b0f19] p-2.5 rounded-lg border border-slate-800">
          <span className="text-slate-400 block mb-0.5">False Alarm Prevention</span>
          <span className="font-bold text-cyan-400 font-mono">
            {faultySensors.length > 0 ? "PASSED (Pipeline Normal)" : "ACTIVE"}
          </span>
        </div>
      </div>
    </div>
  );
};
