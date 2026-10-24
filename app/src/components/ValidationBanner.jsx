import React from 'react';
import { CheckCircle2, AlertTriangle, XCircle, Info } from 'lucide-react';

export default function ValidationBanner({ paper, headerMarks }) {
  if (!paper) return null;

  const totalCalculated = paper.total_marks_calculated;
  const isMarksMatch = Math.abs(totalCalculated - headerMarks) < 0.01;
  const errors = paper.validation_errors || [];
  const warnings = paper.validation_warnings || [];

  return (
    <div className="space-y-2">
      <div className={`p-3 rounded-xl border flex items-center justify-between text-xs transition-all ${
        paper.is_valid && isMarksMatch
          ? 'bg-emerald-50 border-emerald-200 text-emerald-900'
          : 'bg-rose-50 border-rose-200 text-rose-900'
      }`}>
        <div className="flex items-center gap-2">
          {paper.is_valid && isMarksMatch ? (
            <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
          ) : (
            <XCircle className="w-4 h-4 text-rose-600 flex-shrink-0" />
          )}
          <div>
            <span className="font-semibold">
              {paper.is_valid && isMarksMatch ? 'Ready for Export' : 'Export Blocked (Validation Issues)'}
            </span>
            <div className="text-[11px] opacity-80">
              Template: <span className="font-bold">{paper.template === '3b' ? '3b (MCQ Booklet)' : '3a (Theory Paper)'}</span> · 
              Questions: <span className="font-bold">{paper.groups.reduce((acc, g) => acc + g.questions.length, 0)}</span> · 
              Groups: <span className="font-bold">{paper.groups.length}</span>
            </div>
          </div>
        </div>

        <div className="text-right">
          <div className="font-semibold">
            Calculated: <span className={isMarksMatch ? 'text-emerald-700' : 'text-rose-700 font-bold'}>{totalCalculated}</span> / {headerMarks} Marks
          </div>
          <div className="text-[10px] uppercase font-bold tracking-wider">
            {isMarksMatch ? 'Marks Balanced' : 'Marks Mismatch'}
          </div>
        </div>
      </div>

      {errors.length > 0 && (
        <div className="bg-rose-50/80 border border-rose-200 rounded-xl p-3 text-xs text-rose-800 space-y-1">
          <div className="font-semibold flex items-center gap-1.5 text-rose-900">
            <XCircle className="w-3.5 h-3.5" /> Validation Errors:
          </div>
          <ul className="list-disc pl-5 space-y-0.5 text-[11px]">
            {errors.map((err, i) => (
              <li key={i}>{err}</li>
            ))}
          </ul>
        </div>
      )}

      {warnings.length > 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-3 text-xs text-amber-800 space-y-1">
          <div className="font-semibold flex items-center gap-1.5 text-amber-900">
            <AlertTriangle className="w-3.5 h-3.5" /> Notices:
          </div>
          <ul className="list-disc pl-5 space-y-0.5 text-[11px]">
            {warnings.map((warn, i) => (
              <li key={i}>{warn}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
