"use client";

import React from "react";
import { Incident } from "@/types";
import { History, CheckCircle, ShieldAlert, Cpu, Database, Clock, ChevronRight } from "lucide-react";
import Link from "next/link";

interface IncidentHistoryPanelProps {
  incidents: Incident[];
  onAcknowledge: (id: string) => void;
  onResolve: (id: string) => void;
  isHardwareAlertActive?: boolean;
}

export const IncidentHistoryPanel: React.FC<IncidentHistoryPanelProps> = ({
  incidents,
  onAcknowledge,
  onResolve,
  isHardwareAlertActive = false,
}) => {
  return (
    <div className="bg-[#0f172a] border border-slate-800 rounded-xl p-5 shadow-lg space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <History className="w-5 h-5 text-cyan-400" />
          <h3 className="font-bold text-white text-base">Persistent Incident Audit Log & History</h3>
          <span className="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded font-mono">
            {incidents.length} TOTAL RECORDS
          </span>
        </div>

        <Link
          href="/incidents"
          className="text-xs text-cyan-400 hover:text-cyan-300 font-semibold flex items-center gap-1 transition"
        >
          <span>View All Incidents Page</span>
          <ChevronRight className="w-4 h-4" />
        </Link>
      </div>

      {incidents.length === 0 ? (
        <div className="p-6 text-center text-slate-400 text-xs bg-[#0b0f19] rounded-lg border border-slate-800">
          No historical incident logs recorded yet.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-mono text-[11px] uppercase bg-[#0b0f19]">
                <th className="p-3">Incident ID / Source</th>
                <th className="p-3">Event Type & Severity</th>
                <th className="p-3">Segment / Zone</th>
                <th className="p-3">Peak Prototype Input</th>
                <th className="p-3">Timestamps</th>
                <th className="p-3 text-center">Lifecycle Status</th>
                <th className="p-3 text-right">Operator Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-sans">
              {incidents.map((inc) => {
                const isHardware =
                  inc.incident_id.startsWith("INC-HW") ||
                  inc.incident_id.startsWith("INC-ESP32") ||
                  inc.disclaimer?.includes("FSR402");

                const peakAdc = (inc as any).peak_raw_adc;
                const peakPressEq = (inc as any).peak_pressure_equivalent;

                const isCurrentlyActiveAlert = isHardwareAlertActive && inc.status !== "RESOLVED";

                return (
                  <tr key={inc.incident_id} className="hover:bg-slate-800/40 transition">
                    {/* ID & Source */}
                    <td className="p-3 font-mono">
                      <div className="font-bold text-white text-xs">{inc.incident_id}</div>
                      <span
                        className={`inline-flex items-center gap-1 text-[10px] px-1.5 py-0.5 rounded font-mono font-medium mt-1 ${
                          isHardware
                            ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"
                            : "bg-amber-500/10 text-amber-300 border border-amber-500/30"
                        }`}
                      >
                        {isHardware ? (
                          <>
                            <Cpu className="w-3 h-3 text-emerald-400" /> LIVE HARDWARE (ESP32)
                          </>
                        ) : (
                          <>
                            <Database className="w-3 h-3 text-amber-300" /> SIMULATION ENGINE
                          </>
                        )}
                      </span>
                    </td>

                    {/* Event Type & Severity */}
                    <td className="p-3">
                      <div className="font-semibold text-slate-200">{inc.incident_type.replace("_", " ")}</div>
                      <span
                        className={`text-[10px] font-bold font-mono px-1.5 py-0.5 rounded ${
                          inc.severity === "CRITICAL"
                            ? "bg-rose-500/20 text-rose-300 border border-rose-500/40"
                            : inc.severity === "HIGH"
                            ? "bg-amber-500/20 text-amber-300 border border-amber-500/40"
                            : "bg-slate-700 text-slate-300"
                        }`}
                      >
                        {inc.severity}
                      </span>
                    </td>

                    {/* Segment & Zone */}
                    <td className="p-3 font-mono">
                      <div className="text-cyan-400 font-bold">{inc.affected_segment}</div>
                      <div className="text-slate-400 text-[10px]">{inc.affected_zone}</div>
                    </td>

                    {/* Peak Input */}
                    <td className="p-3 font-mono text-[11px]">
                      {isHardware ? (
                        <div>
                          <div className="text-white">Peak ADC: {peakAdc ?? "N/A"}</div>
                          <div className="text-slate-400 text-[10px]">
                            Pressure Eq: {peakPressEq ? `${peakPressEq.toFixed(1)}%` : "N/A"}
                          </div>
                        </div>
                      ) : (
                        <div className="text-slate-400">Flow Loss: {inc.estimated_flow_loss_lpm} LPM</div>
                      )}
                    </td>

                    {/* Timestamps */}
                    <td className="p-3 text-[11px] text-slate-400 font-mono space-y-0.5">
                      <div>Created: {inc.created_at ? new Date(inc.created_at).toLocaleTimeString() : "N/A"}</div>
                      {(inc as any).acknowledged_at && (
                        <div className="text-amber-400">
                          Ack: {new Date((inc as any).acknowledged_at).toLocaleTimeString()}
                        </div>
                      )}
                      {(inc as any).resolved_at && (
                        <div className="text-emerald-400">
                          Res: {new Date((inc as any).resolved_at).toLocaleTimeString()}
                        </div>
                      )}
                    </td>

                    {/* Lifecycle Status Badge */}
                    <td className="p-3 text-center">
                      <span
                        className={`px-2.5 py-1 rounded text-[11px] font-bold font-mono tracking-wide ${
                          inc.status === "OPEN"
                            ? "bg-rose-500/20 text-rose-300 border border-rose-500/40 animate-pulse"
                            : inc.status === "ACKNOWLEDGED"
                            ? "bg-amber-500/20 text-amber-300 border border-amber-500/40"
                            : "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                        }`}
                      >
                        {inc.status}
                      </span>
                    </td>

                    {/* Operator Action Buttons */}
                    <td className="p-3 text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        {inc.status === "OPEN" && (
                          <button
                            onClick={() => onAcknowledge(inc.incident_id)}
                            className="px-2.5 py-1 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold rounded text-[11px] transition shadow-sm"
                            title="Mark incident as seen by operator"
                          >
                            ACKNOWLEDGE
                          </button>
                        )}

                        {inc.status !== "RESOLVED" && (
                          <button
                            disabled={isCurrentlyActiveAlert}
                            onClick={() => onResolve(inc.incident_id)}
                            className={`px-2.5 py-1 font-bold rounded text-[11px] transition shadow-sm ${
                              isCurrentlyActiveAlert
                                ? "bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700"
                                : "bg-emerald-500 hover:bg-emerald-400 text-slate-950"
                            }`}
                            title={
                              isCurrentlyActiveAlert
                                ? "Resolve after sensor returns to NORMAL"
                                : "Close and resolve historical incident"
                            }
                          >
                            RESOLVE
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
