"use client";

import React from "react";
import Link from "next/link";
import {
  Activity,
  ArrowRight,
  ShieldCheck,
  Zap,
  Eye,
  Crosshair,
  TrendingDown,
  Sparkles,
  Database,
  CheckCircle2,
  AlertTriangle,
  Radio,
  Layers,
  Search
} from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#0b0f19] text-slate-100 font-sans selection:bg-cyan-500 selection:text-slate-900">
      {/* Navigation Header */}
      <header className="border-b border-slate-800/80 bg-[#0f172a]/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shadow-[0_0_12px_rgba(6,182,212,0.3)]">
              <Activity className="w-5 h-5" />
            </div>
            <span className="font-bold text-lg text-white tracking-tight">AquaSentinel</span>
            <span className="text-[10px] bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 px-2 py-0.5 rounded font-mono font-medium">
              v1.0 HACKATHON EDITION
            </span>
          </div>

          <div className="flex items-center gap-6 text-sm font-medium">
            <a href="#how-it-works" className="text-slate-400 hover:text-cyan-400 transition">
              How It Works
            </a>
            <a href="#observability" className="text-slate-400 hover:text-cyan-400 transition">
              Observability
            </a>
            <a href="#false-alarms" className="text-slate-400 hover:text-cyan-400 transition">
              False Alarm AI
            </a>
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-2 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold px-4 py-2 rounded-lg transition shadow-[0_0_20px_rgba(6,182,212,0.3)]"
            >
              <span>ENTER LIVE DASHBOARD</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative pt-20 pb-24 overflow-hidden border-b border-slate-800/60">
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-cyan-500/10 rounded-full blur-[140px] pointer-events-none"></div>

        <div className="max-w-5xl mx-auto px-6 text-center relative z-10">
          <div className="inline-flex items-center gap-2 bg-cyan-950/80 border border-cyan-500/30 text-cyan-300 text-xs font-semibold px-3.5 py-1.5 rounded-full mb-6 shadow-sm">
            <Zap className="w-3.5 h-3.5 text-cyan-400" />
            <span>AI-Powered Water Network Intelligence & Resilience</span>
          </div>

          <h1 className="text-4xl md:text-6xl font-extrabold text-white tracking-tight leading-tight mb-6">
            See the Network. Detect the Incident. <br />
            <span className="bg-gradient-to-r from-cyan-400 via-sky-300 to-blue-500 bg-clip-text text-transparent">
              Understand the Risk.
            </span>
          </h1>

          <p className="text-lg md:text-xl text-slate-300 max-w-3xl mx-auto leading-relaxed mb-10">
            AquaSentinel is an AI-powered water-network intelligence platform that detects anomalous behavior, evaluates monitoring blind spots, localizes suspected incidents, estimates model-derived water loss, and helps operators respond with evidence.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/dashboard"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-extrabold px-8 py-4 rounded-xl text-base transition shadow-[0_0_25px_rgba(6,182,212,0.4)]"
            >
              <span>ENTER LIVE DASHBOARD</span>
              <ArrowRight className="w-5 h-5" />
            </Link>
            <a
              href="#how-it-works"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-slate-800/80 hover:bg-slate-800 text-slate-200 font-bold px-8 py-4 rounded-xl text-base border border-slate-700 transition"
            >
              <span>HOW IT WORKS</span>
            </a>
          </div>

          {/* Quick Metrics Bar */}
          <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-4 text-left">
            <div className="bg-[#0f172a]/90 p-4 rounded-xl border border-slate-800">
              <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold block mb-1">
                Canonical Sensors
              </span>
              <span className="text-2xl font-black text-white font-mono">10 Sensors</span>
            </div>
            <div className="bg-[#0f172a]/90 p-4 rounded-xl border border-slate-800">
              <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold block mb-1">
                Pipeline Segments
              </span>
              <span className="text-2xl font-black text-cyan-400 font-mono">10 Segments</span>
            </div>
            <div className="bg-[#0f172a]/90 p-4 rounded-xl border border-slate-800">
              <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold block mb-1">
                Observability Index
              </span>
              <span className="text-2xl font-black text-emerald-400 font-mono">89.7%</span>
            </div>
            <div className="bg-[#0f172a]/90 p-4 rounded-xl border border-slate-800">
              <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold block mb-1">
                False Alarm Prevention
              </span>
              <span className="text-2xl font-black text-amber-400 font-mono">Active</span>
            </div>
          </div>
        </div>
      </section>

      {/* The Problem Section */}
      <section className="py-20 border-b border-slate-800/60 bg-[#0f172a]/40">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-xs font-bold uppercase tracking-widest text-cyan-400 mb-2">The Infrastructure Challenge</h2>
            <h3 className="text-3xl font-extrabold text-white">Why Water Leak Detection Demands Intelligence</h3>
            <p className="text-slate-400 text-sm mt-3">
              Water network anomalies can represent leaks, bursts, sensor faults, or unobservable blind spots. Traditional monitoring detects unusual conditions, but operators still need evidence-backed answers.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-[#0f172a] p-6 rounded-xl border border-slate-800">
              <div className="w-10 h-10 rounded-lg bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-400 mb-4">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <h4 className="font-bold text-white text-base mb-2">Uncertain Leak Localization</h4>
              <p className="text-slate-400 text-xs leading-relaxed">
                When a pressure drop occurs, traditional threshold alerts cannot pinpoint which specific pipe segment is leaking versus experiencing normal consumer demand spikes.
              </p>
            </div>

            <div className="bg-[#0f172a] p-6 rounded-xl border border-slate-800">
              <div className="w-10 h-10 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400 mb-4">
                <Radio className="w-5 h-5" />
              </div>
              <h4 className="font-bold text-white text-base mb-2">Sensor Fault False Alarms</h4>
              <p className="text-slate-400 text-xs leading-relaxed">
                Single sensor electronic spikes often trigger expensive false-alarm field dispatches when the surrounding pipeline network is completely healthy.
              </p>
            </div>

            <div className="bg-[#0f172a] p-6 rounded-xl border border-slate-800">
              <div className="w-10 h-10 rounded-lg bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 mb-4">
                <Eye className="w-5 h-5" />
              </div>
              <h4 className="font-bold text-white text-base mb-2">Monitoring Blind Spots</h4>
              <p className="text-slate-400 text-xs leading-relaxed">
                Operators rarely know how observable each segment of their network is, leaving critical distribution trunks unmonitored without knowing where to add sensors.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works - 6-Stage Connected Architecture Pipeline */}
      <section id="how-it-works" className="py-20 border-b border-slate-800/60">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-xs font-bold uppercase tracking-widest text-cyan-400 mb-2">End-to-End System Pipeline</h2>
            <h3 className="text-3xl font-extrabold text-white">How AquaSentinel Intelligence Works</h3>
            <p className="text-slate-400 text-sm mt-3">
              A six-stage connected architecture processing simulated telemetry into actionable operator response guidance.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                step: "01",
                title: "Telemetry Ingestion",
                desc: "Simulated IoT network sensors provide continuous pressure and flow readings across 10 canonical nodes.",
                icon: Radio,
                color: "text-sky-400"
              },
              {
                step: "02",
                title: "Multi-Signal Detection",
                desc: "Rolling Z-scores, rate-of-change analysis, and Isolation Forest algorithms identify anomalous behavior.",
                icon: Search,
                color: "text-cyan-400"
              },
              {
                step: "03",
                title: "Simulated Observability",
                desc: "NetworkX graph evaluation computes segment observability scores and identifies monitoring blind spots.",
                icon: Eye,
                color: "text-indigo-400"
              },
              {
                step: "04",
                title: "Topology Localization",
                desc: "Correlates responsive sensor pairs to pinpoint affected pipeline segments (e.g. B2-B3) with candidate confidence scores.",
                icon: Crosshair,
                color: "text-rose-400"
              },
              {
                step: "05",
                title: "Loss Estimation",
                desc: "Estimates model-derived flow loss rate (LPM) and accumulated volume loss (liters).",
                icon: TrendingDown,
                color: "text-amber-400"
              },
              {
                step: "06",
                title: "AI Response Guidance",
                desc: "Generates structured evidence summaries, candidate segment uncertainty, and recommended operator actions.",
                icon: Sparkles,
                color: "text-emerald-400"
              }
            ].map((item, idx) => {
              const Icon = item.icon;
              return (
                <div key={idx} className="bg-[#0f172a] p-6 rounded-xl border border-slate-800 relative group hover:border-cyan-500/40 transition">
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-xs font-mono font-bold text-slate-500 group-hover:text-cyan-400 transition">
                      STAGE {item.step}
                    </span>
                    <Icon className={`w-5 h-5 ${item.color}`} />
                  </div>
                  <h4 className="font-bold text-white text-base mb-2">{item.title}</h4>
                  <p className="text-slate-400 text-xs leading-relaxed">{item.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Differentiator Section */}
      <section id="observability" className="py-20 border-b border-slate-800/60 bg-[#0f172a]/40">
        <div className="max-w-6xl mx-auto px-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <div className="inline-flex items-center gap-2 bg-cyan-950 text-cyan-300 border border-cyan-800 text-xs font-semibold px-3 py-1 rounded-full mb-4">
                <Eye className="w-3.5 h-3.5 text-cyan-400" />
                <span>CORE DIFFERENTIATOR</span>
              </div>
              <h2 className="text-3xl font-extrabold text-white mb-4">
                Monitor the Network. <br />
                <span className="text-cyan-400">Monitor the Monitoring.</span>
              </h2>
              <p className="text-slate-300 text-sm leading-relaxed mb-6">
                A network can have healthy sensors and still contain monitoring blind spots. AquaSentinel doesn’t only detect leaks—it evaluates how observable each segment of the network is and identifies candidate virtual sensor placements to eliminate blind spots.
              </p>
              <div className="space-y-3">
                <div className="flex items-center gap-3 text-xs text-slate-300">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                  <span>Calculates model-derived simulated observability index across all 10 canonical segments.</span>
                </div>
                <div className="flex items-center gap-3 text-xs text-slate-300">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                  <span>Identifies low-observability blind spots before unmonitored leaks escalate.</span>
                </div>
                <div className="flex items-center gap-3 text-xs text-slate-300">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                  <span>Evaluates candidate sensor placement to maximize network coverage efficiency.</span>
                </div>
              </div>
            </div>

            <div className="bg-[#0f172a] p-6 rounded-xl border border-slate-800 space-y-4">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Simulated Observability Tiers</h4>
              <div className="p-3 bg-[#0b0f19] rounded-lg border border-slate-800 flex items-center justify-between">
                <div>
                  <span className="text-xs font-bold text-white block">High Observability (B2-B3)</span>
                  <span className="text-[11px] text-slate-400">Multi-sensor correlation & tight node spacing</span>
                </div>
                <span className="text-sm font-mono font-bold text-emerald-400">91.0%</span>
              </div>
              <div className="p-3 bg-[#0b0f19] rounded-lg border border-slate-800 flex items-center justify-between">
                <div>
                  <span className="text-xs font-bold text-white block">Medium Observability (A1-A2)</span>
                  <span className="text-[11px] text-slate-400">Standard two-sensor boundary coverage</span>
                </div>
                <span className="text-sm font-mono font-bold text-amber-400">65.0%</span>
              </div>
              <div className="p-3 bg-[#0b0f19] rounded-lg border border-slate-800 flex items-center justify-between">
                <div>
                  <span className="text-xs font-bold text-white block">Critical Blind Spot (C2-C3)</span>
                  <span className="text-[11px] text-slate-400">Single sensor terminal segment</span>
                </div>
                <span className="text-sm font-mono font-bold text-rose-400">42.0%</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* False Alarm Intelligence Section */}
      <section id="false-alarms" className="py-20 border-b border-slate-800/60">
        <div className="max-w-6xl mx-auto px-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div className="order-2 lg:order-1 bg-[#0f172a] p-6 rounded-xl border border-slate-800 space-y-4">
              <div className="flex items-center justify-between p-3 bg-amber-500/10 border border-amber-500/30 rounded-lg text-amber-300 text-xs font-bold">
                <span className="flex items-center gap-2">
                  <Radio className="w-4 h-4 text-amber-400" /> SENSOR FAULT DEMONSTRATION
                </span>
                <span className="font-mono">Sensor B3 Anomalous</span>
              </div>
              <div className="p-4 bg-[#0b0f19] rounded-lg border border-slate-800 space-y-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-slate-400">Sensor B3 (Faulty):</span>
                  <span className="text-amber-400 font-mono font-bold">5.85 bar (Spike Fault)</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Sensor B2 (Upstream):</span>
                  <span className="text-emerald-400 font-mono font-bold">3.00 bar (Normal)</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Sensor B4 (Downstream):</span>
                  <span className="text-emerald-400 font-mono font-bold">3.00 bar (Normal)</span>
                </div>
                <div className="pt-2 border-t border-slate-800 text-cyan-400 font-semibold">
                  RESULT: SENSOR FAULT CLASSIFIED | 0 False Pipeline Leaks
                </div>
              </div>
            </div>

            <div className="order-1 lg:order-2">
              <div className="inline-flex items-center gap-2 bg-amber-950 text-amber-300 border border-amber-800 text-xs font-semibold px-3 py-1 rounded-full mb-4">
                <ShieldCheck className="w-3.5 h-3.5 text-amber-400" />
                <span>FALSE ALARM INTELLIGENCE</span>
              </div>
              <h2 className="text-3xl font-extrabold text-white mb-4">
                Not Every Anomaly is a Leak.
              </h2>
              <p className="text-slate-300 text-sm leading-relaxed mb-6">
                When an isolated sensor produces abnormal readings while neighboring sensors remain normal, AquaSentinel correctly classifies the event as a <strong>Sensor Fault</strong> instead of triggering a false leak alert on the pipeline network.
              </p>
              <div className="space-y-3">
                <div className="flex items-center gap-3 text-xs text-slate-300">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                  <span>Verifies spatial pressure propagation before declaring a pipe incident.</span>
                </div>
                <div className="flex items-center gap-3 text-xs text-slate-300">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                  <span>Prevents costly false alarm field dispatches and unnecessary pipeline excavation.</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Final Call to Action Section */}
      <section className="py-20 bg-gradient-to-b from-[#0b0f19] to-[#0f172a] text-center">
        <div className="max-w-4xl mx-auto px-6">
          <h2 className="text-3xl md:text-4xl font-extrabold text-white mb-6">
            Ready to Explore AquaSentinel Live?
          </h2>
          <p className="text-slate-300 text-base mb-8 max-w-2xl mx-auto">
            Experience the operational control room, test the gradual leak pulse visualization, evaluate blind spots, and review AI incident guidance.
          </p>
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-2 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-extrabold px-8 py-4 rounded-xl text-base transition shadow-[0_0_30px_rgba(6,182,212,0.5)]"
          >
            <span>ENTER LIVE DASHBOARD NOW</span>
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </section>
    </div>
  );
}
