import React, { useState, useEffect } from 'react';
import { 
  Search, Filter, BookOpen, Layers, CheckCircle2, 
  Calendar, Award, Plus, Sparkles, X, ChevronRight 
} from 'lucide-react';

export default function QuestionBankModal({ isOpen, onClose, onInsertQuestion }) {
  const [questions, setQuestions] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState("");
  const [selectedClass, setSelectedClass] = useState("");
  const [selectedSubject, setSelectedSubject] = useState("");
  const [selectedType, setSelectedType] = useState("");

  const fetchQuestions = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (selectedClass) params.append("class_name", selectedClass);
      if (selectedSubject) params.append("subject", selectedSubject);
      if (selectedType) params.append("q_type", selectedType);
      if (search) params.append("q", search);
      params.append("limit", "100");

      const res = await fetch(`/api/bank/questions?${params.toString()}`);
      const data = await res.json();
      setQuestions(data.items || []);
      setTotal(data.total || 0);
    } catch (err) {
      console.error("Failed to fetch bank questions:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchQuestions();
    }
  }, [isOpen, selectedClass, selectedSubject, selectedType]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchQuestions();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="w-full max-w-5xl h-[88vh] flex flex-col rounded-2xl glass-card overflow-hidden shadow-2xl border border-white/60">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-200/60 bg-white/50 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center text-white shadow-md">
              <BookOpen className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-800 tracking-tight flex items-center gap-2">
                Question Bank Explorer
                <span className="text-[11px] bg-indigo-100 text-indigo-700 font-bold px-2 py-0.5 rounded-full">
                  {total} Questions
                </span>
              </h2>
              <p className="text-xs text-slate-500">
                Search, inspect exam usage history, and insert questions directly into your paper.
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-xl hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Filter Controls Bar */}
        <div className="px-6 py-3 border-b border-slate-200/50 bg-white/40 flex flex-wrap items-center gap-3">
          {/* Search Input */}
          <form onSubmit={handleSearchSubmit} className="flex-1 min-w-[260px] relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search question text, keyword, or chapter..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 text-xs rounded-xl glass-input focus:outline-none"
            />
          </form>

          {/* Type Filter */}
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="px-3 py-1.5 text-xs rounded-xl glass-input font-medium cursor-pointer"
          >
            <option value="">All Question Types</option>
            <option value="MCQ">MCQ (Objective)</option>
            <option value="SHORT">Answer in Brief</option>
            <option value="FIGURE_QA">Figure & Diagram</option>
            <option value="MAP_MARK">Map Work</option>
            <option value="FILL_BLANK">Fill in Blanks</option>
            <option value="TRUE_FALSE">True or False</option>
          </select>

          {/* Class Filter */}
          <select
            value={selectedClass}
            onChange={(e) => setSelectedClass(e.target.value)}
            className="px-3 py-1.5 text-xs rounded-xl glass-input font-medium cursor-pointer"
          >
            <option value="">All Classes</option>
            <option value="Class 9th">Class 9th</option>
            <option value="Class 10th">Class 10th</option>
            <option value="Class 8th">Class 8th</option>
          </select>

          <button
            onClick={fetchQuestions}
            className="px-4 py-1.5 rounded-xl text-xs font-semibold glass-button-primary text-white cursor-pointer"
          >
            Filter
          </button>
        </div>

        {/* Questions List */}
        <div className="flex-1 p-6 overflow-y-auto space-y-3.5 bg-slate-50/30">
          {loading ? (
            <div className="flex items-center justify-center py-24 text-slate-400 gap-2">
              <div className="w-5 h-5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
              <span className="text-sm font-medium">Loading question bank...</span>
            </div>
          ) : questions.length === 0 ? (
            <div className="text-center py-20 text-slate-400">
              <p className="text-sm font-medium">No questions matched the selected criteria.</p>
            </div>
          ) : (
            questions.map((q) => {
              const hasUsage = q.used_in && q.used_in.length > 0;

              return (
                <div
                  key={q.id}
                  className="p-4 rounded-xl glass-card glass-card-hover flex flex-col gap-2.5 transition"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                        {/* Type Badge */}
                        <span className="px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider bg-indigo-100 text-indigo-700">
                          {q.type}
                        </span>
                        {/* Marks Badge */}
                        <span className="px-2 py-0.5 rounded-md text-[10px] font-bold bg-slate-100 text-slate-700">
                          {q.marks} {q.marks === 1 ? 'Mark' : 'Marks'}
                        </span>
                        {/* Class/Subject */}
                        <span className="text-[11px] text-slate-400">
                          {q.class} · {q.subject}
                        </span>
                      </div>

                      {/* Question Text */}
                      <p className="text-sm font-medium text-slate-800 leading-snug">
                        {q.text}
                      </p>

                      {/* Options preview if MCQ */}
                      {q.options && q.options.length === 4 && (
                        <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs text-slate-600 mt-2 pl-2 border-l-2 border-indigo-200">
                          <div>(1) {q.options[0]}</div>
                          <div>(2) {q.options[1]}</div>
                          <div>(3) {q.options[2]}</div>
                          <div>(4) {q.options[3]}</div>
                        </div>
                      )}
                    </div>

                    {/* Action Button */}
                    <button
                      onClick={() => onInsertQuestion(q)}
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold glass-button-secondary text-indigo-600 hover:text-indigo-800 cursor-pointer flex-shrink-0"
                    >
                      <Plus className="w-3.5 h-3.5" /> Insert
                    </button>
                  </div>

                  {/* Usage Badges Footer */}
                  <div className="flex items-center gap-2 pt-2 border-t border-slate-100 text-[11px]">
                    <span className="text-slate-400 font-medium">History:</span>
                    {hasUsage ? (
                      <div className="flex items-center gap-1.5 flex-wrap">
                        {q.used_in.map((u, uIdx) => (
                          <span
                            key={uIdx}
                            className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-amber-50 border border-amber-200 text-amber-800"
                          >
                            <Calendar className="w-2.5 h-2.5" />
                            {u.exam_name} ({u.date})
                          </span>
                        ))}
                      </div>
                    ) : (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-50 border border-emerald-200 text-emerald-700">
                        <Sparkles className="w-2.5 h-2.5" /> Fresh (Never used)
                      </span>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
