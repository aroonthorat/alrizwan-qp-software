import React, { useState, useEffect } from 'react';
import HeaderForm from './components/HeaderForm';
import ValidationBanner from './components/ValidationBanner';
import A4Preview from './components/A4Preview';
import QuestionBankModal from './components/QuestionBankModal';
import AutoPickModal from './components/AutoPickModal';
import TeacherReviewDrawer from './components/TeacherReviewDrawer';
import AdminStatsModal from './components/AdminStatsModal';
import { 
  Download, FileCheck, AlertCircle, RefreshCw, Layers, 
  Sparkles, FileText, CheckCircle2, ChevronRight, BookOpen, 
  Wand2, Database, History, SlidersHorizontal, ShieldCheck,
  Camera, Languages, Coins
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

  // Modals
  const [isBankOpen, setIsBankOpen] = useState(false);
  const [isAutoPickOpen, setIsAutoPickOpen] = useState(false);
  const [isReviewOpen, setIsReviewOpen] = useState(false);
  const [isAdminOpen, setIsAdminOpen] = useState(false);
  const [isBilingualActive, setIsBilingualActive] = useState(false);
  const [ocrLoading, setOcrLoading] = useState(false);

  // Grammar & Review State
  const [autoLogs, setAutoLogs] = useState([]);
  const [suggestions, setSuggestions] = useState([]);

  // Load sample list on startup
  useEffect(() => {
    fetch('/api/samples')
      .then(res => res.json())
      .then(data => {
        setSamples(data);
        if (data.length > 0) {
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
      const chosenKey = keys.includes(activePartKey) ? activePartKey : (keys.includes("theory") ? "theory" : keys[0]);
      setActivePartKey(chosenKey);

      // Trigger Grammar & Style Check on active paper
      if (data.parts && data.parts[chosenKey]) {
        runGrammarCheck(data.parts[chosenKey].paper);
      }
    } catch (err) {
      console.error("Parse failed:", err);
    } finally {
      setLoading(false);
    }
  };

  const runGrammarCheck = async (paperObj) => {
    try {
      const res = await fetch('/api/grammar/check', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ paper: paperObj })
      });
      if (res.ok) {
        const data = await res.json();
        setAutoLogs(data.auto_logs || []);
        setSuggestions(data.suggestions || []);
      }
    } catch (err) {
      console.error("Grammar check error:", err);
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

  const handleExportAnswerKey = async (targetPartKey = activePartKey) => {
    if (!parsedParts || !parsedParts[targetPartKey]) return;
    const currentPaper = parsedParts[targetPartKey].paper;

    try {
      setExporting(true);
      setExportError(null);
      const res = await fetch('/api/export/answer-key', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ paper: currentPaper })
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Answer key export failed");
      }

      const blob = await res.blob();
      const contentDisposition = res.headers.get('Content-Disposition');
      let filename = `${currentPaper.header.class_name} ${currentPaper.header.subject} - Answer Key.docx`;
      if (contentDisposition && contentDisposition.includes('filename=')) {
        const match = contentDisposition.match(/filename="?([^"]+)"?/);
        if (match && match[1]) filename = match[1];
      }

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

  const handleDownloadBackup = async () => {
    try {
      const res = await fetch('/api/backup/create', { method: 'POST' });
      if (!res.ok) throw new Error("Backup failed");
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `alrizwan_backup_${new Date().toISOString().slice(0, 10)}.zip`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Backup error:", err);
    }
  };

  const handleOcrUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setOcrLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await fetch('/api/ocr/upload', {
        method: 'POST',
        body: formData
      });
      if (res.ok) {
        const data = await res.json();
        if (data.text) {
          setRawText(data.text);
          triggerParse(data.text, header, templateOverride);
        }
      }
    } catch (err) {
      console.error("OCR upload error:", err);
    } finally {
      setOcrLoading(false);
      e.target.value = '';
    }
  };

  const handleToggleBilingual = async () => {
    if (!currentPaper) return;
    if (isBilingualActive) {
      setIsBilingualActive(false);
      triggerParse(rawText, header, templateOverride);
      return;
    }

    try {
      setLoading(true);
      const res = await fetch('/api/bilingual/translate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ paper: currentPaper })
      });
      if (res.ok) {
        const data = await res.json();
        const bilingualPaper = data.bilingual_paper;
        setIsBilingualActive(true);
        setParsedParts(prev => ({
          ...prev,
          [activePartKey]: {
            ...prev[activePartKey],
            paper: bilingualPaper,
            sheets: prev[activePartKey].sheets.map(sh => ({
              ...sh,
              groups: bilingualPaper.groups
            }))
          }
        }));
      }
    } catch (err) {
      console.error("Bilingual translate error:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleExportBilingual = async () => {
    if (!currentPaper) return;
    try {
      setExporting(true);
      const res = await fetch('/api/export/bilingual', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ paper: currentPaper })
      });
      if (!res.ok) throw new Error("Bilingual export failed");
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Class ${header.class_name.replace('Class', '').trim()} ${header.subject} - Bilingual Paper.docx`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Bilingual export error:", err);
    } finally {
      setExporting(false);
    }
  };

  const handleInsertFromBank = (q) => {
    let questionSnippet = `\n${q.text}`;
    if (q.options && q.options.length === 4) {
      questionSnippet += `\n(1) ${q.options[0]} (2) ${q.options[1]}\n(3) ${q.options[2]} (4) ${q.options[3]}`;
    }
    const updated = rawText ? `${rawText}\n${questionSnippet}` : questionSnippet;
    setRawText(updated);
    triggerParse(updated, header, templateOverride);
  };

  const handleAutoPickComplete = (data) => {
    const newPaper = data.paper;
    setHeader(newPaper.header);
    setTemplateOverride(newPaper.template);
    
    let formatted = "";
    newPaper.groups.forEach(g => {
      formatted += `${g.heading}\n`;
      g.questions.forEach(q => {
        formatted += `${q.q_num}. ${q.text}\n`;
        if (q.options && q.options.length === 4) {
          formatted += `(1) ${q.options[0]} (2) ${q.options[1]}\n(3) ${q.options[2]} (4) ${q.options[3]}\n`;
        }
      });
      formatted += "\n";
    });
    setRawText(formatted);

    const key = newPaper.template === '3b' ? 'mcq' : 'theory';
    setActivePartKey(key);
    setParsedParts({
      [key]: {
        paper: newPaper,
        sheets: data.sheets,
        logo_data_uri: data.logo_data_uri
      }
    });
    runGrammarCheck(newPaper);
  };

  const handleApplySuggestion = (sugg) => {
    if (!sugg.suggestion) return;
    const regex = new RegExp(escapeRegex(sugg.original), 'g');
    const updated = rawText.replace(regex, sugg.suggestion);
    setRawText(updated);
    triggerParse(updated, header, templateOverride);
    setSuggestions(prev => prev.filter(s => s !== sugg));
  };

  const handleApplyAllSuggestions = () => {
    let updated = rawText;
    suggestions.forEach(sugg => {
      if (sugg.suggestion) {
        const regex = new RegExp(escapeRegex(sugg.original), 'g');
        updated = updated.replace(regex, sugg.suggestion);
      }
    });
    setRawText(updated);
    triggerParse(updated, header, templateOverride);
    setSuggestions([]);
  };

  const handleAddToDictionary = async (word, lang) => {
    try {
      await fetch('/api/grammar/dictionary/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ word, lang })
      });
      setSuggestions(prev => prev.filter(s => s.original !== word));
    } catch (err) {
      console.error("Failed to add word to dictionary:", err);
    }
  };

  function escapeRegex(str) {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  const currentActive = parsedParts && parsedParts[activePartKey] ? parsedParts[activePartKey] : null;
  const currentPaper = currentActive ? currentActive.paper : null;
  const currentSheets = currentActive ? currentActive.sheets : [];
  const logoDataUri = currentActive ? currentActive.logo_data_uri : null;

  return (
    <div className="min-h-screen liquid-ambient-bg flex flex-col font-sans">
      {/* Liquid Frosted Glass Top Navbar */}
      <header className="px-6 py-3.5 glass-card border-b border-white/40 sticky top-0 z-40 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-1 rounded-xl bg-white/80 shadow-xs border border-white/60">
            <img src="/assets/logo.jpg" alt="School Logo" className="w-8 h-8 object-contain rounded-lg" />
          </div>
          <div>
            <div className="font-extrabold text-slate-900 text-sm tracking-tight flex items-center gap-2">
              Al-Rizwan Question Paper Software
              <span className="text-[10px] bg-gradient-to-r from-emerald-500/15 to-indigo-500/15 text-emerald-800 font-extrabold px-2.5 py-0.5 rounded-full border border-emerald-200/50 uppercase tracking-wider">
                Phase 3
              </span>
            </div>
            <div className="text-[11px] text-slate-500 font-medium">
              Offline First · Grammar Engine (en/hi/mr/ur) · Question Bank & History · Word 2007 Export
            </div>
          </div>
        </div>

        {/* Action Controls Bar */}
        <div className="flex items-center gap-2.5">
          {/* Grammar & Style Review Button */}
          <button
            onClick={() => setIsReviewOpen(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold glass-button-secondary text-slate-700 hover:text-emerald-700 cursor-pointer"
          >
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
            <span>Grammar & Review</span>
            {suggestions.length > 0 && (
              <span className="text-[10px] bg-amber-500 text-white px-1.5 py-0.2 rounded-full font-extrabold">
                {suggestions.length}
              </span>
            )}
          </button>

          {/* Question Bank Explorer Button */}
          <button
            onClick={() => setIsBankOpen(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold glass-button-secondary text-slate-700 hover:text-indigo-600 cursor-pointer"
          >
            <BookOpen className="w-3.5 h-3.5 text-indigo-600" /> Question Bank
          </button>

          {/* Blueprint Auto-Pick Button */}
          <button
            onClick={() => setIsAutoPickOpen(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold glass-button-secondary text-slate-700 hover:text-amber-600 cursor-pointer"
          >
            <Wand2 className="w-3.5 h-3.5 text-amber-500" /> Auto-Pick
          </button>

          {/* Backup Database Button */}
          <button
            onClick={handleDownloadBackup}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold glass-button-secondary text-slate-700 hover:text-sky-600 cursor-pointer"
            title="Download full database backup archive (.zip)"
          >
            <Database className="w-3.5 h-3.5 text-sky-600" /> Backup
          </button>

          {/* AI Console / Admin Stats Button */}
          <button
            onClick={() => setIsAdminOpen(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold glass-button-secondary text-slate-700 hover:text-purple-600 cursor-pointer"
            title="Open Cloudflare D1 & AI Gateway Console"
          >
            <Coins className="w-3.5 h-3.5 text-purple-600" /> AI Console
          </button>

          {/* Sample Selector */}
          <div className="flex items-center gap-1.5 glass-card rounded-xl px-2.5 py-1 text-xs">
            <span className="text-slate-400 font-medium">Sample:</span>
            <select
              className="bg-transparent font-semibold text-slate-700 focus:outline-none cursor-pointer"
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

          {/* Export Question Paper Button */}
          <button
            onClick={() => handleExport(activePartKey)}
            disabled={!currentPaper || !currentPaper.is_valid || exporting}
            className={`flex items-center gap-2 px-3.5 py-2 rounded-xl font-bold text-xs shadow-md transition cursor-pointer ${
              currentPaper && currentPaper.is_valid && !exporting
                ? 'glass-button-primary text-white cursor-pointer active:scale-95'
                : 'bg-slate-200/70 text-slate-400 border border-slate-300/40 cursor-not-allowed'
            }`}
            title={
              currentPaper && !currentPaper.is_valid
                ? currentPaper.validation_errors.join('\n')
                : 'Export Question Paper (.docx)'
            }
          >
            <Download className="w-4 h-4" />
            {exporting ? 'Generating...' : 'Export Paper (.docx)'}
          </button>

          {/* Export Answer Key Button */}
          <button
            onClick={() => handleExportAnswerKey(activePartKey)}
            disabled={!currentPaper || exporting}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl font-bold text-xs glass-button-secondary text-slate-700 hover:text-indigo-700 shadow-xs transition cursor-pointer"
            title="Generate and download Answer Key (.docx)"
          >
            <FileCheck className="w-4 h-4 text-emerald-600" />
            <span>Answer Key</span>
          </button>

          {/* Export Bilingual Button */}
          <button
            onClick={handleExportBilingual}
            disabled={!currentPaper || exporting}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl font-bold text-xs glass-button-secondary text-slate-700 hover:text-purple-700 shadow-xs transition cursor-pointer"
            title="Export Bilingual Paper (.docx) with Urdu Nastaleeq"
          >
            <Languages className="w-4 h-4 text-purple-600" />
            <span>Bilingual .docx</span>
          </button>
        </div>
      </header>

      {/* Main Workspace Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Column: Form + Input Editor */}
        <aside className="w-[490px] p-4 flex flex-col gap-4 overflow-y-auto max-h-[calc(100vh-65px)]">
          {/* Header Form */}
          <HeaderForm
            header={header}
            onChange={(newHeader) => {
              setHeader(newHeader);
              triggerParse(rawText, newHeader, templateOverride);
            }}
          />

          {/* Question Input Box */}
          <div className="p-4 rounded-2xl glass-card flex flex-col flex-1">
            <div className="flex items-center justify-between mb-2">
              <label className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5 text-indigo-600" /> Pasted Questions
              </label>
              <div className="flex items-center gap-2.5">
                <label className="text-[11px] font-bold text-purple-600 hover:text-purple-800 flex items-center gap-1 cursor-pointer">
                  <Camera className="w-3.5 h-3.5" />
                  <span>{ocrLoading ? 'Scanning...' : 'Photo / OCR'}</span>
                  <input
                    type="file"
                    accept="image/*"
                    className="hidden"
                    onChange={handleOcrUpload}
                    disabled={ocrLoading}
                  />
                </label>
                <button
                  onClick={() => triggerParse(rawText, header, templateOverride)}
                  disabled={loading}
                  className="text-[11px] font-bold text-indigo-600 hover:text-indigo-800 flex items-center gap-1 cursor-pointer"
                >
                  <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} /> Re-Parse
                </button>
              </div>
            </div>

            <textarea
              className="w-full flex-1 min-h-[220px] p-3 text-xs font-mono rounded-xl glass-input leading-relaxed resize-y"
              placeholder="Paste question paper text here (e.g. Q.1) Answer the following... or 1. Stem (1) Opt1 (2) Opt2...)"
              value={rawText}
              onChange={(e) => {
                setRawText(e.target.value);
                triggerParse(e.target.value, header, templateOverride);
              }}
            />

            {/* Template Selector Controls */}
            <div className="mt-3 pt-3 border-t border-slate-200/50 flex items-center justify-between text-xs">
              <span className="text-slate-500 font-semibold">Layout Template:</span>
              <div className="flex gap-1.5 p-0.5 rounded-xl glass-card">
                <button
                  onClick={() => {
                    setTemplateOverride(null);
                    triggerParse(rawText, header, null);
                  }}
                  className={`px-2.5 py-1 rounded-lg text-[11px] font-bold transition cursor-pointer ${
                    templateOverride === null
                      ? 'bg-slate-800 text-white shadow-xs'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  Auto
                </button>
                <button
                  onClick={() => {
                    setTemplateOverride('3a');
                    triggerParse(rawText, header, '3a');
                  }}
                  className={`px-2.5 py-1 rounded-lg text-[11px] font-bold transition cursor-pointer ${
                    (templateOverride === '3a' || (!templateOverride && currentPaper?.template === '3a'))
                      ? 'bg-indigo-600 text-white shadow-xs'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  3a Theory
                </button>
                <button
                  onClick={() => {
                    setTemplateOverride('3b');
                    triggerParse(rawText, header, '3b');
                  }}
                  className={`px-2.5 py-1 rounded-lg text-[11px] font-bold transition cursor-pointer ${
                    (templateOverride === '3b' || (!templateOverride && currentPaper?.template === '3b'))
                      ? 'bg-indigo-600 text-white shadow-xs'
                      : 'text-slate-600 hover:text-slate-900'
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
            <div className="p-3 rounded-2xl bg-rose-500/15 border border-rose-300 text-rose-900 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0" />
              <span>{exportError}</span>
            </div>
          )}
        </aside>

        {/* Right Column: Multi-part tabs & Live A4 Preview Canvas */}
        <main className="flex-1 p-6 flex flex-col items-center overflow-y-auto">
          {/* Paper View Controls Toolbar */}
          <div className="mb-4 flex items-center gap-3">
            {parsedParts && Object.keys(parsedParts).length > 1 && (
              <div className="p-1 rounded-2xl glass-card flex items-center gap-1 shadow-xs">
                {Object.keys(parsedParts).map((partKey) => {
                  const part = parsedParts[partKey].paper;
                  const isSelected = activePartKey === partKey;
                  return (
                    <button
                      key={partKey}
                      onClick={() => {
                        setActivePartKey(partKey);
                        runGrammarCheck(part);
                      }}
                      className={`px-3 py-1.5 rounded-xl text-xs font-bold flex items-center gap-2 transition cursor-pointer ${
                        isSelected
                          ? 'glass-button-primary text-white'
                          : 'text-slate-600 hover:text-slate-900 hover:bg-white/40'
                      }`}
                    >
                      <span>{partKey === 'mcq' ? 'MCQ Paper (3b)' : 'Theory Paper (3a)'}</span>
                      <span className={`text-[10px] px-1.5 py-0.2 rounded font-extrabold ${
                        part.is_valid ? 'bg-emerald-500/20 text-emerald-800' : 'bg-rose-500/20 text-rose-800'
                      }`}>
                        {part.total_marks_calculated}M
                      </span>
                    </button>
                  );
                })}
              </div>
            )}

            {/* Bilingual Mode Toggle Button */}
            <button
              onClick={handleToggleBilingual}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-bold flex items-center gap-1.5 transition cursor-pointer ${
                isBilingualActive
                  ? 'bg-purple-600 text-white shadow-md'
                  : 'glass-button-secondary text-slate-700 hover:text-purple-700'
              }`}
              title="Toggle English ⇄ Urdu stacked bilingual view"
            >
              <Languages className={`w-3.5 h-3.5 ${isBilingualActive ? 'text-white' : 'text-purple-600'}`} />
              <span>{isBilingualActive ? 'Bilingual Active (اردو / En)' : 'Switch to Bilingual (اردو)'}</span>
            </button>
          </div>

          {/* Live A4 Preview Canvas */}
          <A4Preview
            paper={currentPaper}
            sheets={currentSheets}
            logoDataUri={logoDataUri}
          />
        </main>
      </div>

      {/* Cloudflare & AI Admin Console Modal */}
      <AdminStatsModal
        isOpen={isAdminOpen}
        onClose={() => setIsAdminOpen(false)}
      />

      {/* Question Bank Explorer Modal */}
      <QuestionBankModal
        isOpen={isBankOpen}
        onClose={() => setIsBankOpen(false)}
        onInsertQuestion={handleInsertFromBank}
      />

      {/* Blueprint Auto-Pick Modal */}
      <AutoPickModal
        isOpen={isAutoPickOpen}
        onClose={() => setIsAutoPickOpen(false)}
        header={header}
        onAutoPickComplete={handleAutoPickComplete}
      />

      {/* Teacher Review Drawer */}
      <TeacherReviewDrawer
        isOpen={isReviewOpen}
        onClose={() => setIsReviewOpen(false)}
        paper={currentPaper}
        autoLogs={autoLogs}
        suggestions={suggestions}
        onApplySuggestion={handleApplySuggestion}
        onApplyAll={handleApplyAllSuggestions}
        onAddToDictionary={handleAddToDictionary}
      />
    </div>
  );
}
