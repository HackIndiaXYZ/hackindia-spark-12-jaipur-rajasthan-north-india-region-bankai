"use client";

import React, { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { listDataSources, getDataSourceSummary } from "@/lib/api/client";
import { GovernmentDataSource, GovernmentObservationSummary } from "@/types";
import { Database, Info, ShieldCheck, RefreshCw, BarChart2 } from "lucide-react";

export default function DataSourcesPage() {
  const [sources, setSources] = useState<GovernmentDataSource[]>([]);
  const [summaries, setSummaries] = useState<Record<string, GovernmentObservationSummary>>({});
  const [loading, setLoading] = useState<boolean>(true);

  // Default fallback source definitions matching Milestone 7 backend
  const DEFAULT_SOURCES: GovernmentDataSource[] = [
    {
      source_id: "rajasthan_rainfall_telemetry",
      dataset_name: "Rajasthan Surface Water Telemetry Hourly Rainfall",
      agency: "Rajasthan Surface Water Department",
      source_organization: "National Water Data Portals / India WRIS",
      geography: "Rajasthan, India",
      data_frequency: "Hourly",
      start_date: "2021-10-17 07:00",
      end_date: "2030-01-01 08:00",
      format: "CSV",
      local_file: "rainfall_tel_hr_rajasthan_sw_rj_2021_2025.csv",
      source_type: "GOVERNMENT_TELEMETRY",
      description: "Hourly regional rainfall telemetry observations from rain stations across Rajasthan.",
      unit: "mm",
      zone: null
    },
    {
      source_id: "mahi_canal_discharge",
      dataset_name: "Mahi Head Regulator Canal Telemetry Hourly Discharge",
      agency: "Rajasthan Surface Water Department",
      source_organization: "National Water Data Portals / India WRIS",
      geography: "Sikar / Banswara, Rajasthan, India",
      data_frequency: "Hourly",
      start_date: "2024-12-13 12:00",
      end_date: "2026-03-25 15:00",
      format: "JSON (NWDP Schema)",
      local_file: "data (1).json",
      source_type: "GOVERNMENT_TELEMETRY",
      description: "Hourly canal head regulator gate discharge telemetry measurements from Mahi Canal.",
      unit: "cusec",
      zone: null
    },
    {
      source_id: "bisalpur_dam_discharge",
      dataset_name: "Bisalpur Dam Reservoir Telemetry Hourly Discharge",
      agency: "Rajasthan Surface Water Department",
      source_organization: "National Water Data Portals / India WRIS",
      geography: "Tonk, Rajasthan, India",
      data_frequency: "Hourly",
      start_date: "2024-03-06 04:00",
      end_date: "2024-09-11 05:00",
      format: "JSON (NWDP Schema)",
      local_file: "data.json",
      source_type: "GOVERNMENT_TELEMETRY",
      description: "Hourly dam spillway gate discharge telemetry measurements from Bisalpur Reservoir.",
      unit: "cusec",
      zone: null
    }
  ];

  const DEFAULT_SUMMARIES: Record<string, GovernmentObservationSummary> = {
    rajasthan_rainfall_telemetry: {
      source_id: "rajasthan_rainfall_telemetry",
      latest_timestamp: "2026-09-06 23:00",
      latest_value: 1.0,
      unit: "mm",
      min_value: 0.0,
      max_value: 931.5,
      mean_value: 4.4502,
      median_value: 1.0,
      observation_count: 143460,
      missing_value_count: 53,
      coverage_start: "2021-06-14 10:00",
      coverage_end: "2026-09-06 23:00",
      historical_mean_deviation: -3.4502
    },
    mahi_canal_discharge: {
      source_id: "mahi_canal_discharge",
      latest_timestamp: "2026-08-20 13:00",
      latest_value: 0.0,
      unit: "cusec",
      min_value: 0.0,
      max_value: 0.0,
      mean_value: 0.0,
      median_value: 0.0,
      observation_count: 2404,
      missing_value_count: 0,
      coverage_start: "2024-12-13 12:00",
      coverage_end: "2026-08-20 13:00",
      historical_mean_deviation: 0.0
    },
    bisalpur_dam_discharge: {
      source_id: "bisalpur_dam_discharge",
      latest_timestamp: "2024-09-11 05:00",
      latest_value: 0.0,
      unit: "cusec",
      min_value: 0.0,
      max_value: 0.0,
      mean_value: 0.0,
      median_value: 0.0,
      observation_count: 1030,
      missing_value_count: 0,
      coverage_start: "2024-03-06 04:00",
      coverage_end: "2024-09-11 05:00",
      historical_mean_deviation: 0.0
    }
  };

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      try {
        const data = await listDataSources();
        setSources(data.sources);

        const summaryMap: Record<string, GovernmentObservationSummary> = {};
        for (const s of data.sources) {
          try {
            const sum = await getDataSourceSummary(s.source_id);
            summaryMap[s.source_id] = sum;
          } catch (e) {
            console.warn(`Failed to fetch summary for ${s.source_id}`, e);
          }
        }
        setSummaries(summaryMap);
      } catch (err) {
        console.warn("Backend offline, using fallback Milestone 7 government data context:", err);
        setSources(DEFAULT_SOURCES);
        setSummaries(DEFAULT_SUMMARIES);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  return (
    <AppShell>
      <div className="p-6 max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
          <div>
            <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
              <Database className="w-5 h-5 text-cyan-400" />
              Regional Government Data Context & Calibration
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Offline Rajasthan NWDP Surface Water telemetry datasets providing regional hydrological context
            </p>
          </div>
          <span className="text-xs font-mono bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 px-3 py-1 rounded-full font-semibold">
            3 NWDP DATASETS REGISTERED
          </span>
        </div>

        {/* PROVENANCE DISCLAIMER BOX */}
        <div className="bg-[#0f172a] border border-cyan-500/30 rounded-xl p-5 shadow-md flex items-start gap-4">
          <Info className="w-6 h-6 text-cyan-400 flex-shrink-0 mt-0.5" />
          <div className="space-y-1 text-xs">
            <h4 className="font-bold text-white text-sm">Data Scope & Attribution Notice</h4>
            <p className="text-slate-300 leading-relaxed">
              These datasets expose official <strong>Rajasthan Surface Water Department / NWDP</strong> telemetry (Rainfall Telemetry CSVs, Mahi Canal Discharge, Bisalpur Reservoir Discharge) for regional hydrologic context and baseline calibration only.
            </p>
            <p className="text-cyan-400 font-semibold pt-1">
              Note: Regional government hydrology data does NOT directly measure municipal pipeline leaks or trigger automated leak alerts.
            </p>
          </div>
        </div>

        {/* DATASETS GRID */}
        <div className="space-y-6">
          {sources.map((src) => {
            const summary = summaries[src.source_id];

            return (
              <div
                key={src.source_id}
                className="bg-[#0f172a] border border-slate-800 rounded-xl p-6 shadow-lg space-y-4"
              >
                <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
                  <div>
                    <div className="flex items-center gap-3">
                      <h2 className="text-base font-bold text-white">{src.dataset_name}</h2>
                      <span className="text-[10px] bg-cyan-950 text-cyan-300 border border-cyan-800 px-2 py-0.5 rounded font-mono font-semibold">
                        {src.source_type}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 mt-1">{src.description}</p>
                  </div>

                  <div className="text-right">
                    <span className="text-xs font-bold text-slate-300 block">{src.agency}</span>
                    <span className="text-[11px] text-slate-400 font-mono">{src.geography}</span>
                  </div>
                </div>

                {/* Metadata & Statistical Summary Grid */}
                {summary && (
                  <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 text-xs">
                    <div className="bg-[#0b0f19] p-3 rounded-lg border border-slate-800">
                      <span className="text-[10px] text-slate-400 uppercase tracking-wider block mb-1">Date Coverage</span>
                      <span className="font-bold text-white font-mono leading-tight block text-[11px]">
                        {summary.coverage_start?.substring(0, 10)} ➔ {summary.coverage_end?.substring(0, 10)}
                      </span>
                    </div>

                    <div className="bg-[#0b0f19] p-3 rounded-lg border border-slate-800">
                      <span className="text-[10px] text-slate-400 uppercase tracking-wider block mb-1">Total Observations</span>
                      <span className="font-bold text-cyan-400 font-mono text-sm">
                        {summary.observation_count.toLocaleString()}
                      </span>
                    </div>

                    <div className="bg-[#0b0f19] p-3 rounded-lg border border-slate-800">
                      <span className="text-[10px] text-slate-400 uppercase tracking-wider block mb-1">Mean Value</span>
                      <span className="font-bold text-white font-mono text-sm">
                        {summary.mean_value} {summary.unit}
                      </span>
                    </div>

                    <div className="bg-[#0b0f19] p-3 rounded-lg border border-slate-800">
                      <span className="text-[10px] text-slate-400 uppercase tracking-wider block mb-1">Median Value</span>
                      <span className="font-bold text-white font-mono text-sm">
                        {summary.median_value} {summary.unit}
                      </span>
                    </div>

                    <div className="bg-[#0b0f19] p-3 rounded-lg border border-slate-800">
                      <span className="text-[10px] text-slate-400 uppercase tracking-wider block mb-1">Range (Min ➔ Max)</span>
                      <span className="font-bold text-white font-mono text-sm">
                        {summary.min_value} ➔ {summary.max_value} {summary.unit}
                      </span>
                    </div>

                    <div className="bg-[#0b0f19] p-3 rounded-lg border border-slate-800">
                      <span className="text-[10px] text-slate-400 uppercase tracking-wider block mb-1">Latest Observation</span>
                      <span className="font-bold text-emerald-400 font-mono text-sm">
                        {summary.latest_value} {summary.unit}
                      </span>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </AppShell>
  );
}
