import React from 'react';
import { Calendar, Clock, Award, BookOpen, GraduationCap, FileText } from 'lucide-react';

export default function HeaderForm({ header, onChange }) {
  const handleChange = (field, value) => {
    onChange({ ...header, [field]: value });
  };

  return (
    <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
      <div className="flex items-center gap-2 mb-3 pb-2 border-b border-slate-100">
        <GraduationCap className="w-5 h-5 text-indigo-600" />
        <h2 className="font-semibold text-slate-800 text-sm tracking-wide uppercase">Paper Header Details</h2>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
        <div>
          <label className="block text-slate-500 font-medium mb-1">Class</label>
          <input
            type="text"
            className="w-full px-2.5 py-1.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 font-medium"
            value={header.class_name}
            onChange={(e) => handleChange('class_name', e.target.value)}
            placeholder="e.g. Class 9th"
          />
        </div>

        <div>
          <label className="block text-slate-500 font-medium mb-1">Subject</label>
          <input
            type="text"
            className="w-full px-2.5 py-1.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 font-medium"
            value={header.subject}
            onChange={(e) => handleChange('subject', e.target.value)}
            placeholder="e.g. Social Science"
          />
        </div>

        <div>
          <label className="block text-slate-500 font-medium mb-1">Exam / Paper Title</label>
          <input
            type="text"
            className="w-full px-2.5 py-1.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 font-medium"
            value={header.paper_name}
            onChange={(e) => handleChange('paper_name', e.target.value)}
            placeholder="e.g. FIRST UNIT TEST"
          />
        </div>

        <div>
          <label className="block text-slate-500 font-medium mb-1">Month & Year</label>
          <input
            type="text"
            className="w-full px-2.5 py-1.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 font-medium"
            value={header.month_year}
            onChange={(e) => handleChange('month_year', e.target.value)}
            placeholder="e.g. AUG. 2026"
          />
        </div>

        <div>
          <label className="block text-slate-500 font-medium mb-1">Date</label>
          <input
            type="date"
            className="w-full px-2.5 py-1.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 font-medium"
            value={header.date || ''}
            onChange={(e) => handleChange('date', e.target.value)}
          />
        </div>

        <div>
          <label className="block text-slate-500 font-medium mb-1">Total Marks</label>
          <input
            type="number"
            className="w-full px-2.5 py-1.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 font-semibold text-indigo-700"
            value={header.marks}
            onChange={(e) => handleChange('marks', parseInt(e.target.value) || 0)}
          />
        </div>

        <div>
          <label className="block text-slate-500 font-medium mb-1">Duration / Time</label>
          <input
            type="text"
            className="w-full px-2.5 py-1.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 font-medium"
            value={header.time}
            onChange={(e) => handleChange('time', e.target.value)}
            placeholder="e.g. 2 Hours"
          />
        </div>

        <div>
          <label className="block text-slate-500 font-medium mb-1">Roll No. Boxes</label>
          <input
            type="number"
            min="2"
            max="6"
            className="w-full px-2.5 py-1.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 font-medium"
            value={header.roll_no_boxes}
            onChange={(e) => handleChange('roll_no_boxes', parseInt(e.target.value) || 4)}
          />
        </div>
      </div>
    </div>
  );
}
