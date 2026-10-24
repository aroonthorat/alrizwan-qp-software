import React, { useState } from 'react';
import { Sparkles, Wand2, BookOpen, Layers, X, Check } from 'lucide-react';

export default function AutoPickModal({ isOpen, onClose, header, onAutoPickComplete }) {
  const [template, setTemplate] = useState("3a");
  const [count, setCount] = useState(10);
  const [preferredType, setPreferredType] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  if (!isOpen) return null;

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('/api/bank/auto-pick', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          header,
          template,
          question_count: count,
          preferred_type: preferredType || null
        })
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Auto-pick failed");
      }

      const data = await res.json();
      onAutoPickComplete(data);
      onClose();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="w-full max-w-md rounded-2xl glass-card overflow-hidden shadow-2xl border border-white/60 p-6 flex flex-col gap-4">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-200/60">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-amber-500 to-indigo-600 flex items-center justify-center text-white shadow-md">
              <Wand2 className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-bold text-slate-800 text-sm">Blueprint Auto-Pick</h3>
              <p className="text-[11px] text-slate-500">Auto-generate paper from question bank</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-slate-600">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Form Fields */}
        <div className="space-y-3.5 text-xs">
          <div>
            <label className="block text-slate-600 font-semibold mb-1">Target Template</label>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => {
                  setTemplate("3a");
                  setPreferredType("");
                }}
                className={`py-2 px-3 rounded-xl border text-center font-semibold transition cursor-pointer ${
                  template === "3a"
                    ? "bg-indigo-600 text-white border-indigo-600 shadow-sm"
                    : "glass-button-secondary text-slate-700"
                }`}
              >
                Template 3a (Theory)
              </button>
              <button
                type="button"
                onClick={() => {
                  setTemplate("3b");
                  setPreferredType("MCQ");
                }}
                className={`py-2 px-3 rounded-xl border text-center font-semibold transition cursor-pointer ${
                  template === "3b"
                    ? "bg-indigo-600 text-white border-indigo-600 shadow-sm"
                    : "glass-button-secondary text-slate-700"
                }`}
              >
                Template 3b (MCQ)
              </button>
            </div>
          </div>

          <div>
            <label className="block text-slate-600 font-semibold mb-1">Number of Questions</label>
            <div className="flex gap-2">
              {[5, 10, 20, 25, 40].map((num) => (
                <button
                  key={num}
                  type="button"
                  onClick={() => setCount(num)}
                  className={`flex-1 py-1.5 rounded-lg border text-center font-bold text-xs transition cursor-pointer ${
                    count === num
                      ? "bg-slate-800 text-white border-slate-800"
                      : "glass-button-secondary text-slate-600"
                  }`}
                >
                  {num}
                </button>
              ))}
            </div>
          </div>

          {template === "3a" && (
            <div>
              <label className="block text-slate-600 font-semibold mb-1">Filter by Specific Type (Optional)</label>
              <select
                value={preferredType}
                onChange={(e) => setPreferredType(e.target.value)}
                className="w-full px-3 py-2 rounded-xl glass-input font-medium"
              >
                <option value="">Balanced Mix (All Types)</option>
                <option value="SHORT">Short / Brief Questions</option>
                <option value="FIGURE_QA">Figure-based Questions</option>
                <option value="MAP_MARK">Map Work Questions</option>
                <option value="FILL_BLANK">Fill in Blanks</option>
              </select>
            </div>
          )}

          <div className="p-3 rounded-xl bg-indigo-50/70 border border-indigo-100 text-[11px] text-indigo-900 leading-relaxed">
            <span className="font-bold">Least-Recently-Used Rule:</span> Selects questions with the oldest exam dates first or questions that have never been used, preventing repetitive exams.
          </div>

          {error && (
            <div className="p-2.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-[11px]">
              {error}
            </div>
          )}
        </div>

        {/* Action Button */}
        <div className="pt-2">
          <button
            onClick={handleGenerate}
            disabled={loading}
            className="w-full py-2.5 px-4 rounded-xl glass-button-primary text-white font-bold text-xs flex items-center justify-center gap-2 cursor-pointer"
          >
            <Sparkles className="w-4 h-4" />
            {loading ? "Selecting Questions..." : `Generate ${count}-Question Paper`}
          </button>
        </div>
      </div>
    </div>
  );
}
