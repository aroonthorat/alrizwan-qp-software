import React from 'react';
import { Calendar, Clock, Award, BookOpen, GraduationCap, FileText } from 'lucide-react';

export default function HeaderForm({ header, onChange }) {
  const handleChange = (field, value) => {
    onChange({ ...header, [field]: value });
  };

  return (
    <div className="p-4 rounded-2xl glass-card transition-all">
      <div className="flex items-center gap-2 mb-3 pb-2 border-b border-slate-200/50">
        <div className="w-6 h-6 rounded-lg bg-indigo-500/10 flex items-center justify-center text-indigo-600">
          <GraduationCap className="w-4 h-4" />
        </div>
        <h2 className="font-bold text-slate-800 text-xs tracking-wider uppercase">Paper Header Details</h2>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-2.5 text-xs">
        <div>
          <label className="block text-slate-500 font-semibold mb-1 text-[11px]">Class</label>
          <input
            type="text"
            className="w-full px-2.5 py-1.5 rounded-xl glass-input font-medium"
            value={header.class_name}
            onChange={(e) => handleChange('class_name', e.target.value)}
            placeholder="e.g. Class 9th"
          />
        </div>

        <div>
          <label className="block text-slate-500 font-semibold mb-1 text-[11px]">Subject</label>
          <input
            type="text"
            className="w-full px-2.5 py-1.5 rounded-xl glass-input font-medium"
            value={header.subject}
            onChange={(e) => handleChange('subject', e.target.value)}
            placeholder="e.g. Social Science"
          />
        </div>

        <div>
          <label className="block text-slate-500 font-semibold mb-1 text-[11px]">Exam Title</label>
          <input
            type="text"
            className="w-full px-2.5 py-1.5 rounded-xl glass-input font-medium"
            value={header.paper_name}
            onChange={(e) => handleChange('paper_name', e.target.value)}
            placeholder="e.g. FIRST UNIT TEST"
          />
        </div>

        <div>
          <label className="block text-slate-500 font-semibold mb-1 text-[11px]">Month & Year</label>
          <input
            type="text"
            className="w-full px-2.5 py-1.5 rounded-xl glass-input font-medium"
            value={header.month_year}
            onChange={(e) => handleChange('month_year', e.target.value)}
            placeholder="e.g. AUG. 2026"
          />
        </div>

        <div>
          <label className="block text-slate-500 font-semibold mb-1 text-[11px]">Date</label>
          <input
            type="date"
            className="w-full px-2.5 py-1.5 rounded-xl glass-input font-medium"
            value={header.date || ''}
            onChange={(e) => handleChange('date', e.target.value)}
          />
        </div>

        <div>
          <label className="block text-slate-500 font-semibold mb-1 text-[11px]">Max Marks</label>
          <input
            type="number"
            className="w-full px-2.5 py-1.5 rounded-xl glass-input font-bold text-indigo-700"
            value={header.marks}
            onChange={(e) => handleChange('marks', parseInt(e.target.value) || 0)}
          />
        </div>

        <div>
          <label className="block text-slate-500 font-semibold mb-1 text-[11px]">Duration / Time</label>
          <input
            type="text"
            className="w-full px-2.5 py-1.5 rounded-xl glass-input font-medium"
            value={header.time}
            onChange={(e) => handleChange('time', e.target.value)}
            placeholder="e.g. 2 Hours"
          />
        </div>

        <div>
          <label className="block text-slate-500 font-semibold mb-1 text-[11px]">Roll No. Boxes</label>
          <input
            type="number"
            min="2"
            max="6"
            className="w-full px-2.5 py-1.5 rounded-xl glass-input font-medium"
            value={header.roll_no_boxes}
            onChange={(e) => handleChange('roll_no_boxes', parseInt(e.target.value) || 4)}
          />
        </div>
      </div>
    </div>
  );
}
