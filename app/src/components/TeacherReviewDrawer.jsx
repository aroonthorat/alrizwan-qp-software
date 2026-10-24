import React, { useState } from 'react';
import { 
  Sparkles, Check, CheckCheck, X, AlertTriangle, 
  HelpCircle, BookPlus, ArrowRight, ShieldCheck, ChevronDown, ChevronUp 
} from 'lucide-react';

export default function TeacherReviewDrawer({
  isOpen,
  onClose,
  paper,
  autoLogs = [],
  suggestions = [],
  onApplySuggestion,
  onApplyAll,
  onAddToDictionary
}) {
  const [activeTab, setActiveTab] = useState("suggestions"); // "suggestions" or "auto"
  const [expandedLog, setExpandedLog] = useState(false);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="w-full max-w-4xl h-[85vh] rounded-2xl glass-card overflow-hidden shadow-2xl border border-white/60 flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-200/60 bg-white/50 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-emerald-500 to-indigo-600 flex items-center justify-center text-white shadow-md">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-800 tracking-tight flex items-center gap-2">
                Teacher Review Workspace
                <span className="text-[11px] bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded-full">
                  {suggestions.length} Suggestions · {autoLogs.length} Auto-Fixed
                </span>
              </h2>
              <p className="text-xs text-slate-500">
                Rule engine suggestions across English, Hindi, Marathi, and Urdu. Never auto-replaces teacher wording.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {suggestions.length > 0 && (
              <button
                onClick={onApplyAll}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold glass-button-primary text-white cursor-pointer"
              >
                <CheckCheck className="w-3.5 h-3.5" /> Accept All
              </button>
            )}
            <button
              onClick={onClose}
              className="p-1.5 rounded-xl hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Tab Switcher */}
        <div className="px-6 py-2.5 border-b border-slate-200/50 bg-white/40 flex items-center gap-2">
          <button
            onClick={() => setActiveTab("suggestions")}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 cursor-pointer ${
              activeTab === "suggestions"
                ? "bg-slate-800 text-white shadow-xs"
                : "text-slate-600 hover:bg-slate-100"
            }`}
          >
            <span>Review Suggestions</span>
            <span className="text-[10px] bg-amber-500 text-white px-1.5 py-0.2 rounded-full font-extrabold">
              {suggestions.length}
            </span>
          </button>

          <button
            onClick={() => setActiveTab("auto")}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 cursor-pointer ${
              activeTab === "auto"
                ? "bg-slate-800 text-white shadow-xs"
                : "text-slate-600 hover:bg-slate-100"
            }`}
          >
            <span>Mechanical Auto-Fixes</span>
            <span className="text-[10px] bg-emerald-500 text-white px-1.5 py-0.2 rounded-full font-extrabold">
              {autoLogs.length}
            </span>
          </button>
        </div>

        {/* Content Body */}
        <div className="flex-1 p-6 overflow-y-auto space-y-3 bg-slate-50/30">
          {activeTab === "suggestions" ? (
            suggestions.length === 0 ? (
              <div className="text-center py-24 text-slate-400 flex flex-col items-center gap-2">
                <ShieldCheck className="w-10 h-10 text-emerald-500/80" />
                <p className="text-sm font-semibold text-slate-700">No wording or grammar issues found!</p>
                <p className="text-xs text-slate-400">All questions comply with school spelling & grammar rules.</p>
              </div>
            ) : (
              suggestions.map((sugg, i) => (
                <div
                  key={i}
                  className="p-4 rounded-xl glass-card glass-card-hover border-l-4 border-l-amber-500 flex flex-col gap-2.5"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="px-2 py-0.5 rounded-md text-[10px] font-extrabold uppercase bg-amber-100 text-amber-800">
                          {sugg.rule} ({sugg.level})
                        </span>
                        <span className="text-xs text-slate-400 font-medium">
                          Question {sugg.question_id}
                        </span>
                      </div>

                      {/* Explanation */}
                      <p className="text-xs font-semibold text-slate-800 mb-2">
                        {sugg.note}
                      </p>

                      {/* Before / After */}
                      <div className="flex items-center gap-3 p-2.5 rounded-lg bg-slate-100/70 border border-slate-200/70 text-xs">
                        <span className="line-through text-rose-700 font-medium">
                          {sugg.original}
                        </span>
                        <ArrowRight className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
                        <span className="font-bold text-emerald-700">
                          {sugg.suggestion || 'Flagged for inspection'}
                        </span>
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex flex-col gap-1.5 flex-shrink-0">
                      {sugg.suggestion && (
                        <button
                          onClick={() => onApplySuggestion(sugg)}
                          className="flex items-center justify-center gap-1 px-3 py-1.5 rounded-lg text-xs font-bold glass-button-primary text-white cursor-pointer"
                        >
                          <Check className="w-3.5 h-3.5" /> Accept
                        </button>
                      )}
                      <button
                        onClick={() => onAddToDictionary(sugg.original, sugg.lang || 'en')}
                        className="flex items-center justify-center gap-1 px-2.5 py-1 rounded-lg text-[11px] font-semibold glass-button-secondary text-slate-600 hover:text-indigo-600 cursor-pointer"
                        title="Add word to school whitelist so it won't be flagged in future papers"
                      >
                        <BookPlus className="w-3 h-3" /> Whitelist
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )
          ) : (
            /* Auto-Fix Logs */
            <div className="space-y-2">
              <div className="p-3 rounded-xl bg-emerald-50/70 border border-emerald-200/70 text-xs text-emerald-900 mb-3">
                <span className="font-bold">Specs §0 Golden Rule:</span> Mechanical spacing, punctuation, and Unicode normalization rules are applied silently to ensure clean typography and prevent Word 2007 display bugs.
              </div>
              {autoLogs.map((log, idx) => (
                <div key={idx} className="p-3 rounded-xl glass-card flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2.5">
                    <span className="px-2 py-0.5 rounded-md text-[10px] font-extrabold bg-emerald-100 text-emerald-800">
                      {log.rule}
                    </span>
                    <span className="text-slate-700 font-medium">{log.note}</span>
                  </div>
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                    Auto-Applied
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
