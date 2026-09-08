"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Network,
  AlertTriangle,
  Radio,
  Database,
  Home,
  Activity,
  Server,
  Play,
  ShieldAlert,
  Zap,
  Info
} from "lucide-react";
import { useDemo } from "@/context/DemoContext";
import { ScenarioType } from "@/types";

export const AppShell: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const pathname = usePathname();
  const { scenario, setScenario, isBackendLive, isDemoMode, setIsDemoMode } = useDemo();
  const [utcTime, setUtcTime] = useState<string>("");

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setUtcTime(now.toISOString().replace("T", " ").substring(0, 19) + " UTC");
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  // Landing page has no operational sidebar
  const isLandingPage = pathname === "/";

  if (isLandingPage) {
    return <>{children}</>;
  }

  const navItems = [
    { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
    { href: "/network", label: "Network Topology", icon: Network },
    { href: "/incidents", label: "Incidents", icon: AlertTriangle },
    { href: "/sensors", label: "Sensors", icon: Radio },
    { href: "/data-sources", label: "Government Context", icon: Database },
    { href: "/", label: "Landing Page", icon: Home }
  ];

  return (
    <div className="flex h-screen bg-[#0b0f19] text-slate-100 font-sans overflow-hidden">
      {/* Left Sidebar */}
      <aside className="w-64 bg-[#0f172a] border-r border-slate-800 flex flex-col justify-between z-20">
        <div>
          {/* Logo Header */}
          <div className="p-5 border-b border-slate-800/80 flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shadow-[0_0_12px_rgba(6,182,212,0.2)]">
              <Activity className="w-5 h-5" />
            </div>
            <div>
              <h1 className="font-bold tracking-tight text-white text-base leading-none">AquaSentinel</h1>
              <p className="text-[10px] text-cyan-400 font-medium tracking-wider uppercase mt-1">
                Network Intelligence
              </p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="p-3 space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-all ${
                    isActive
                      ? "bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shadow-sm"
                      : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? "text-cyan-400" : "text-slate-400"}`} />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Demo Controller Footer inside Sidebar */}
        <div className="p-4 m-3 bg-[#1e293b]/50 border border-slate-700/60 rounded-lg space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
              <Play className="w-3.5 h-3.5 text-cyan-400" /> Scenario Control
            </span>
            <span className="text-[10px] bg-cyan-500/20 text-cyan-300 px-1.5 py-0.5 rounded font-mono">
              LIVE DEMO
            </span>
          </div>

          <select
            value={scenario}
            onChange={(e) => setScenario(e.target.value as ScenarioType)}
            className="w-full bg-[#0f172a] text-xs text-slate-200 border border-slate-700 rounded-md p-2 focus:outline-none focus:border-cyan-500 cursor-pointer font-medium"
          >
            <option value="normal">Scenario A: Normal Operation</option>
            <option value="gradual_leak">Scenario B: Gradual Leak (B2-B3)</option>
            <option value="sudden_burst">Scenario C: Sudden Burst (Zone B)</option>
            <option value="sensor_fault">Scenario D: Sensor Fault (B3)</option>
          </select>

          <p className="text-[11px] text-slate-400 leading-tight">
            {scenario === "normal" && "Network operational. Baseline pressure & flow."}
            {scenario === "gradual_leak" && "Leak developing on B2-B3. Visually highlights pipe."}
            {scenario === "sudden_burst" && "Severe burst on Zone B. High loss flow rate."}
            {scenario === "sensor_fault" && "Sensor B3 fault. False alarm prevented."}
          </p>
        </div>
      </aside>

      {/* Main Content Container */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Operational Header */}
        <header className="h-14 bg-[#0f172a]/90 backdrop-blur-md border-b border-slate-800 px-6 flex items-center justify-between z-10">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-slate-400">SYSTEM:</span>
              <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                SYSTEM OPERATIONAL
              </span>
            </div>

            {/* Mode Indicator Pill */}
            {isDemoMode ? (
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-mono font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/30">
                <Zap className="w-3 h-3 text-amber-400" /> DEMO MODE
              </span>
            ) : (
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-mono font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
                <Server className="w-3 h-3 text-cyan-400" /> REAL BACKEND API
              </span>
            )}
          </div>

          <div className="flex items-center gap-4">
            {/* Backend Connection Status */}
            <div className="flex items-center gap-2 text-xs">
              <Server className="w-3.5 h-3.5 text-slate-400" />
              <span className="text-slate-400">Backend API:</span>
              {isBackendLive ? (
                <span className="text-emerald-400 font-medium">CONNECTED (Port 8000)</span>
              ) : (
                <span className="text-amber-400 font-medium">OFFLINE (Using Demo State)</span>
              )}
            </div>

            {/* Toggle Demo vs Backend Mode */}
            {isBackendLive && (
              <button
                onClick={() => setIsDemoMode(!isDemoMode)}
                className="text-xs px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded border border-slate-700 transition"
              >
                Switch to {isDemoMode ? "Real API" : "Demo Mode"}
              </button>
            )}

            {/* Clock */}
            <div className="text-xs font-mono text-slate-400 bg-[#0b0f19] px-3 py-1 rounded border border-slate-800">
              {utcTime || "2026-09-08 08:00:00 UTC"}
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto bg-[#0b0f19]">{children}</main>
      </div>
    </div>
  );
};
