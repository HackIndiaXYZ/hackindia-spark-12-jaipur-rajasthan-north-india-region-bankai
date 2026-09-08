"use client";

import React from "react";
import { Sparkles, CheckCircle2, ShieldAlert, HelpCircle, Info } from "lucide-react";

interface AIAnalysisPanelProps {
  whyDetected: string[];
  recommendedActions: string[];
  confidenceNote: string;
  limitations: string;
  isSensorFault?: boolean;
}

export const AIAnalysisPanel: React.FC<AIAnalysisPanelProps> = ({
  whyDetected,
  recommendedActions,
  confidenceNote,
  limitations,
  isSensorFault = false
}) => {
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
            <p className="text-xs text-slate-400">Contextual evidence interpretation & operator decision support</p>
          </div>
        </div>
        <span className="text-[10px] bg-cyan-950 text-cyan-300 border border-cyan-800 px-2.5 py-1 rounded-full font-mono font-semibold">
          AI EXPLAINABILITY ENGINE
        </span>
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
