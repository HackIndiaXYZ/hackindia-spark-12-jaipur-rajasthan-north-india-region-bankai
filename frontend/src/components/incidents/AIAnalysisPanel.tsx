"use client";

import React, { useState, useEffect } from "react";
import { Sparkles, CheckCircle2, ShieldAlert, HelpCircle, Info, RefreshCw, Cpu } from "lucide-react";
import { getAIAnalysis } from "@/lib/api/client";

interface AIAnalysisPanelProps {
  incidentId?: string;
  whyDetected?: string[];
  recommendedActions?: string[];
  confidenceNote?: string;
  limitations?: string;
  isSensorFault?: boolean;
  provider?: string;
}

export const AIAnalysisPanel: React.FC<AIAnalysisPanelProps> = ({
  incidentId,
  whyDetected: initialWhy,
  recommendedActions: initialActions,
  confidenceNote: initialConfidence,
  limitations: initialLimitations,
  isSensorFault = false,
  provider: initialProvider = "gemini"
}) => {
  const [loading, setLoading] = useState<boolean>(false);
  const [whyDetected, setWhyDetected] = useState<string[]>(initialWhy || []);
  const [recommendedActions, setRecommendedActions] = useState<string[]>(initialActions || []);
  const [confidenceNote, setConfidenceNote] = useState<string>(initialConfidence || "");
  const [limitations, setLimitations] = useState<string>(initialLimitations || "");
  const [provider, setProvider] = useState<string>(initialProvider);

  // Sync props if initial props change
  useEffect(() => {
    if (initialWhy) setWhyDetected(initialWhy);
    if (initialActions) setRecommendedActions(initialActions);
    if (initialConfidence) setConfidenceNote(initialConfidence);
    if (initialLimitations) setLimitations(initialLimitations);
    if (initialProvider) setProvider(initialProvider);
  }, [initialWhy, initialActions, initialConfidence, initialLimitations, initialProvider]);

  // Request AI analysis explicitly when requested or incidentId changes
  const fetchAIAnalysis = async () => {
    if (!incidentId) return;
    setLoading(true);
    try {
      const res = await getAIAnalysis(incidentId);
      setWhyDetected(res.analysis.why_detected);
      setRecommendedActions(res.analysis.recommended_actions);
      setConfidenceNote(res.analysis.confidence_note);
      setLimitations(res.analysis.limitations);
      setProvider(res.provider);
    } catch (err) {
      console.warn("Failed to fetch real AI analysis, using provided state:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-[#0f172a] border border-cyan-500/30 rounded-xl p-5 shadow-lg relative overflow-hidden">
      {/* Decorative Cyan Accent Corner */}
      <div className="absolute top-0 right-0 w-32 h-32 bg-cyan-500/5 rounded-full blur-2xl pointer-events-none"></div>

      {/* Header */}
      <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-800">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center text-cyan-400">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-bold text-white text-base">AI Incident Analysis & Guidance</h3>
            <p className="text-xs text-slate-400">Grounded evidence interpretation & operator decision support</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {incidentId && (
            <button
              onClick={fetchAIAnalysis}
              disabled={loading}
              className="inline-flex items-center gap-1 text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 px-2.5 py-1 rounded border border-slate-700 transition"
              title="Request Fresh AI Analysis"
            >
              <RefreshCw className={`w-3 h-3 text-cyan-400 ${loading ? "animate-spin" : ""}`} />
              <span>{loading ? "Analyzing..." : "Analyze"}</span>
            </button>
          )}

          <span className={`text-[10px] px-2.5 py-1 rounded-full font-mono font-semibold border ${
            provider === "gemini"
              ? "bg-cyan-950 text-cyan-300 border-cyan-800"
              : "bg-slate-800 text-slate-300 border-slate-700"
          }`}>
            {provider === "gemini" ? "✨ GEMINI 2.5 FLASH AI" : "⚙️ DETERMINISTIC FALLBACK"}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Why Detected / Classified */}
        <div className="bg-[#0b0f19] p-4 rounded-lg border border-slate-800">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 mb-3 flex items-center gap-2">
            <HelpCircle className="w-3.5 h-3.5 text-cyan-400" />
            {isSensorFault ? "Why Classified as Sensor Fault" : "Why Detected as Network Incident"}
          </h4>
          <ul className="space-y-2">
            {whyDetected.map((reason, idx) => (
              <li key={idx} className="flex items-start gap-2 text-xs text-slate-300 leading-relaxed">
                <span className="text-cyan-400 font-bold">•</span>
                <span>{reason}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Recommended Actions */}
        <div className="bg-[#0b0f19] p-4 rounded-lg border border-slate-800">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 mb-3 flex items-center gap-2">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            Recommended Operator Actions
          </h4>
          <ul className="space-y-2">
            {recommendedActions.map((action, idx) => (
              <li key={idx} className="flex items-start gap-2 text-xs text-slate-300 leading-relaxed">
                <span className="text-emerald-400 font-bold">{idx + 1}.</span>
                <span>{action}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Footer Disclaimer & Confidence Breakdown */}
      <div className="mt-4 pt-4 border-t border-slate-800/80 grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
        <div className="flex items-center gap-2 text-slate-400">
          <Info className="w-4 h-4 text-cyan-400 flex-shrink-0" />
          <span>{confidenceNote}</span>
        </div>
        <div className="flex items-center gap-2 text-slate-400 bg-amber-500/5 p-2 rounded border border-amber-500/20">
          <ShieldAlert className="w-4 h-4 text-amber-400 flex-shrink-0" />
          <span className="text-[11px] leading-tight">{limitations}</span>
        </div>
      </div>
    </div>
  );
};
