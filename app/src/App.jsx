import React, { useState, useEffect } from 'react';
import HeaderForm from './components/HeaderForm';
import ValidationBanner from './components/ValidationBanner';
import A4Preview from './components/A4Preview';
import { 
  Download, FileCheck, AlertCircle, RefreshCw, Layers, 
  Sparkles, FileText, CheckCircle2, ChevronRight 
} from 'lucide-react';

export default function App() {
  const [header, setHeader] = useState({
    school: "Al-Rizwan English School",
    address: "Chaitaniya Nagar Road, Nanded",
    class_name: "Class 9th",
    subject: "Social Science",
    paper_name: "FIRST UNIT TEST",
    month_year: "AUG. 2026",
    date: "2026-08-12",
    marks: 40,
    time: "2 Hours",
    roll_no_boxes: 4
  });

  const [rawText, setRawText] = useState("");
  const [samples, setSamples] = useState([]);
  const [selectedSample, setSelectedSample] = useState("");
  const [parsedParts, setParsedParts] = useState(null);
  const [activePartKey, setActivePartKey] = useState("theory");
  const [templateOverride, setTemplateOverride] = useState(null);
  const [loading, setLoading] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [exportError, setExportError] = useState(null);

  // Load sample list on startup
  useEffect(() => {
    fetch('/api/samples')
      .then(res => res.json())
      .then(data => {
        setSamples(data);
        if (data.length > 0) {
          // Pre-load the first sample
          loadSampleContent(data[0].name);
        }
      })
      .catch(err => console.error("Could not load samples:", err));
  }, []);

  const loadSampleContent = async (filename) => {
    setSelectedSample(filename);
    try {
      setLoading(true);
      const res = await fetch(`/api/samples/${filename}`);
      const data = await res.json();
      setRawText(data.content);
      // Automatically trigger parse
      triggerParse(data.content, header, templateOverride);
    } catch (err) {
      console.error("Failed to load sample:", err);
    } finally {
      setLoading(false);
    }
  };

  const triggerParse = async (content, currentHeader, tOverride = null) => {
    if (!content.trim()) return;
    setLoading(true);
    setExportError(null);
    try {
      const res = await fetch('/api/parse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          header: currentHeader,
          content: content,
          template_override: tOverride
        })
      });
      const data = await res.json();
      setParsedParts(data.parts);

      // Select initial active part
      const keys = Object.keys(data.parts);
      if (keys.includes(activePartKey)) {
        // keep current
      } else if (keys.includes("theory")) {
        setActivePartKey("theory");
      } else {
        setActivePartKey(keys[0]);
      }
    } catch (err) {
      console.error("Parse failed:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (targetPartKey = activePartKey) => {
    if (!parsedParts || !parsedParts[targetPartKey]) return;
    const currentPaper = parsedParts[targetPartKey].paper;

    if (!currentPaper.is_valid) {
      setExportError("Export blocked: Please fix validation errors before exporting.");
      return;
    }

    try {
      setExporting(true);
      setExportError(null);
      const res = await fetch('/api/export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ paper: currentPaper })
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Export failed");
      }

      const blob = await res.blob();
      const contentDisposition = res.headers.get('Content-Disposition');
      let filename = `${currentPaper.header.class_name} ${currentPaper.header.subject} - ${
        currentPaper.template === '3b' ? 'MCQ Paper.docx' : 'Theory Paper.docx'
      }`;
      if (contentDisposition && contentDisposition.includes('filename=')) {
        const match = contentDisposition.match(/filename="?([^"]+)"?/);
        if (match && match[1]) filename = match[1];
      }

      // Trigger browser download
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setExportError(err.message);
    } finally {
      setExporting(false);
    }
  };

  const currentActive = parsedParts && parsedParts[activePartKey] ? parsedParts[activePartKey] : null;
  const currentPaper = currentActive ? currentActive.paper : null;
  const currentSheets = currentActive ? currentActive.sheets : [];
  const logoDataUri = currentActive ? currentActive.logo_data_uri : null;

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col font-sans">
      {/* Top Navbar */}
      <header className="bg-white border-b border-slate-200 px-6 py-3 flex items-center justify-between sticky top-0 z-50 shadow-sm">
        <div className="flex items-center gap-3">
          <img src="/assets/logo.jpg" alt="School Logo" className="w-9 h-9 object-contain rounded" />
          <div>
            <div className="font-bold text-slate-900 text-sm tracking-tight flex items-center gap-2">
              Al-Rizwan Question Paper Software
              <span className="text-[10px] bg-indigo-100 text-indigo-700 font-bold px-2 py-0.5 rounded-full uppercase tracking-wider">
                Phase 1
              </span>
            </div>
            <div className="text-[11px] text-slate-500">
              Offline First · Locked A4 Templates (3a Theory / 3b MCQ) · Word 2007 Compatible
            </div>
          </div>
        </div>

        {/* Right Action Bar */}
        <div className="flex items-center gap-3">
          {/* Sample Loader */}
          <div className="flex items-center gap-1.5 bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1 text-xs">
            <span className="text-slate-500 font-medium">Sample:</span>
            <select
              className="bg-transparent font-medium text-slate-700 focus:outline-none cursor-pointer"
              value={selectedSample}
              onChange={(e) => loadSampleContent(e.target.value)}
            >
              {samples.map((s) => (
                <option key={s.name} value={s.name}>
                  {s.title}
                </option>
              ))}
            </select>
          </div>

          {/* Export Button */}
          <button
            onClick={() => handleExport(activePartKey)}
            disabled={!currentPaper || !currentPaper.is_valid || exporting}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg font-semibold text-xs transition-all shadow-sm ${
              currentPaper && currentPaper.is_valid && !exporting
                ? 'bg-indigo-600 hover:bg-indigo-700 text-white cursor-pointer active:scale-95'
                : 'bg-slate-200 text-slate-400 cursor-not-allowed'
            }`}
            title={
              currentPaper && !currentPaper.is_valid
                ? currentPaper.validation_errors.join('\n')
                : 'Export to Word (.docx)'
            }
          >
            <Download className="w-4 h-4" />
            {exporting ? 'Generating .docx...' : 'Export to Word (.docx)'}
          </button>
        </div>
      </header>

      {/* Main Workspace Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Column: Form + Input Editor */}
        <aside className="w-[480px] border-r border-slate-200 bg-slate-50/50 p-4 flex flex-col gap-4 overflow-y-auto max-h-[calc(100vh-65px)]">
          {/* Header Form */}
          <HeaderForm
            header={header}
            onChange={(newHeader) => {
              setHeader(newHeader);
              triggerParse(rawText, newHeader, templateOverride);
            }}
          />

          {/* Question Input Box */}
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col flex-1">
            <div className="flex items-center justify-between mb-2">
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-700 flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5 text-indigo-600" /> Pasted Questions
              </label>
              <button
                onClick={() => triggerParse(rawText, header, templateOverride)}
                disabled={loading}
                className="text-[11px] font-semibold text-indigo-600 hover:text-indigo-800 flex items-center gap-1 cursor-pointer"
              >
                <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} /> Re-Parse
              </button>
            </div>

            <textarea
              className="w-full flex-1 min-h-[220px] p-3 text-xs font-mono border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 leading-relaxed resize-y bg-slate-50/30"
              placeholder="Paste question paper text here (e.g. Q.1) Answer the following... or 1. Stem (1) Opt1 (2) Opt2...)"
              value={rawText}
              onChange={(e) => {
                setRawText(e.target.value);
                triggerParse(e.target.value, header, templateOverride);
              }}
            />

            {/* Template Selector Controls */}
            <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
              <span className="text-slate-500 font-medium">Layout Template:</span>
              <div className="flex gap-1.5">
                <button
                  onClick={() => {
                    setTemplateOverride(null);
                    triggerParse(rawText, header, null);
                  }}
                  className={`px-2 py-1 rounded text-[11px] font-semibold transition ${
                    templateOverride === null
                      ? 'bg-slate-800 text-white shadow-xs'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  Auto
                </button>
                <button
                  onClick={() => {
                    setTemplateOverride('3a');
                    triggerParse(rawText, header, '3a');
                  }}
                  className={`px-2 py-1 rounded text-[11px] font-semibold transition ${
                    (templateOverride === '3a' || (!templateOverride && currentPaper?.template === '3a'))
                      ? 'bg-indigo-600 text-white shadow-xs'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  3a Theory
                </button>
                <button
                  onClick={() => {
                    setTemplateOverride('3b');
                    triggerParse(rawText, header, '3b');
                  }}
                  className={`px-2 py-1 rounded text-[11px] font-semibold transition ${
                    (templateOverride === '3b' || (!templateOverride && currentPaper?.template === '3b'))
                      ? 'bg-indigo-600 text-white shadow-xs'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  3b MCQ
                </button>
              </div>
            </div>
          </div>

          {/* Validation Notice Banner */}
          <ValidationBanner paper={currentPaper} headerMarks={header.marks} />

          {exportError && (
            <div className="bg-rose-50 border border-rose-200 text-rose-800 p-3 rounded-xl text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0" />
              <span>{exportError}</span>
            </div>
          )}
        </aside>

        {/* Right Column: Multi-part tabs & Live A4 Preview Canvas */}
        <main className="flex-1 bg-slate-200/80 p-6 flex flex-col items-center overflow-y-auto">
          {/* Multi-part tabs if both Theory and MCQ were detected */}
          {parsedParts && Object.keys(parsedParts).length > 1 && (
            <div className="mb-4 bg-white/90 backdrop-blur p-1 rounded-xl shadow-xs border border-slate-300/80 flex items-center gap-1">
              {Object.keys(parsedParts).map((partKey) => {
                const part = parsedParts[partKey].paper;
                const isSelected = activePartKey === partKey;
                return (
                  <button
                    key={partKey}
                    onClick={() => setActivePartKey(partKey)}
                    className={`px-4 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-2 transition cursor-pointer ${
                      isSelected
                        ? 'bg-indigo-600 text-white shadow'
                        : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                    }`}
                  >
                    <span>{partKey === 'mcq' ? 'MCQ Paper (Template 3b)' : 'Theory Paper (Template 3a)'}</span>
                    <span className={`text-[10px] px-1.5 py-0.2 rounded font-bold ${
                      part.is_valid ? 'bg-emerald-500/20 text-emerald-100' : 'bg-rose-500/20 text-rose-100'
                    }`}>
                      {part.total_marks_calculated}M
                    </span>
                  </button>
                );
              })}
            </div>
          )}

          {/* Live A4 Preview */}
          <A4Preview
            paper={currentPaper}
            sheets={currentSheets}
            logoDataUri={logoDataUri}
          />
        </main>
      </div>
    </div>
  );
}
