import React from 'react';
import { CheckCircle2, AlertTriangle, XCircle, History, Sparkles } from 'lucide-react';

export default function ValidationBanner({ paper, headerMarks }) {
  if (!paper) return null;

  const totalCalculated = paper.total_marks_calculated;
  const isMarksMatch = Math.abs(totalCalculated - headerMarks) < 0.01;
  const errors = paper.validation_errors || [];
  const warnings = paper.validation_warnings || [];

  return (
    <div className="space-y-2">
      {/* Primary Validation Status Pill */}
      <div className={`p-3.5 rounded-2xl border backdrop-blur-md flex items-center justify-between text-xs transition-all shadow-sm ${
        paper.is_valid && isMarksMatch
          ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-950'
          : 'bg-rose-500/10 border-rose-500/30 text-rose-950'
      }`}>
        <div className="flex items-center gap-2.5">
          <div className={`w-7 h-7 rounded-xl flex items-center justify-center flex-shrink-0 ${
            paper.is_valid && isMarksMatch ? 'bg-emerald-500 text-white shadow-xs' : 'bg-rose-500 text-white shadow-xs'
          }`}>
            {paper.is_valid && isMarksMatch ? (
              <CheckCircle2 className="w-4 h-4" />
            ) : (
              <XCircle className="w-4 h-4" />
            )}
          </div>
          <div>
            <span className="font-bold tracking-tight text-xs">
              {paper.is_valid && isMarksMatch ? 'Ready for Export' : 'Export Blocked (Validation Issues)'}
            </span>
            <div className="text-[11px] opacity-75 font-medium">
              Template: <span className="font-bold">{paper.template === '3b' ? '3b (MCQ Booklet)' : '3a (Theory Paper)'}</span> · 
              Questions: <span className="font-bold">{paper.groups.reduce((acc, g) => acc + g.questions.length, 0)}</span> · 
              Groups: <span className="font-bold">{paper.groups.length}</span>
            </div>
          </div>
        </div>

        <div className="text-right">
          <div className="font-bold text-xs">
            Calculated: <span className={isMarksMatch ? 'text-emerald-700' : 'text-rose-700'}>{totalCalculated}</span> / {headerMarks} Marks
          </div>
          <div className={`text-[10px] uppercase font-extrabold tracking-wider ${
            isMarksMatch ? 'text-emerald-600' : 'text-rose-600'
          }`}>
            {isMarksMatch ? 'Marks Balanced' : 'Marks Mismatch'}
          </div>
        </div>
      </div>

      {/* Validation Errors */}
      {errors.length > 0 && (
        <div className="bg-rose-500/15 border border-rose-400/40 backdrop-blur-md rounded-2xl p-3 text-xs text-rose-900 space-y-1">
          <div className="font-bold flex items-center gap-1.5 text-rose-950 text-[11px]">
            <XCircle className="w-3.5 h-3.5 text-rose-600" /> Export Blocking Errors:
          </div>
          <ul className="list-disc pl-5 space-y-0.5 text-[11px] opacity-90">
            {errors.map((err, i) => (
              <li key={i}>{err}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Historical Repetition & Style Warnings */}
      {warnings.length > 0 && (
        <div className="bg-amber-500/15 border border-amber-400/40 backdrop-blur-md rounded-2xl p-3 text-xs text-amber-950 space-y-1.5">
          <div className="font-bold flex items-center gap-1.5 text-amber-950 text-[11px]">
            <History className="w-3.5 h-3.5 text-amber-600" /> Exam Usage & Repetition Warnings:
          </div>
          <ul className="list-disc pl-5 space-y-1 text-[11px] opacity-90 max-h-36 overflow-y-auto pr-1">
            {warnings.map((warn, i) => (
              <li key={i}>{warn}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
