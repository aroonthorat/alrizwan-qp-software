import React, { useState, useEffect } from 'react';
import { 
  X, Coins, TrendingUp, Cpu, Database, Cloud, 
  CloudOff, RefreshCw, Trash2, Shield, CheckCircle2, 
  AlertCircle, Sliders 
} from 'lucide-react';

export default function AdminStatsModal({ isOpen, onClose }) {
  const [stats, setStats] = useState(null);
  const [syncStatus, setSyncStatus] = useState(null);
  const [dictionary, setDictionary] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('spend'); // 'spend' | 'sync' | 'dictionary'
  const [newCap, setNewCap] = useState(500);
  const [capMsg, setCapMsg] = useState('');

  const loadData = async () => {
    setLoading(true);
    try {
      const [statsRes, syncRes, dictRes] = await Promise.all([
        fetch('/api/admin/ai-stats'),
        fetch('/api/sync/status'),
        fetch('/api/admin/dictionary')
      ]);

      if (statsRes.ok) {
        const sData = await statsRes.json();
        setStats(sData);
        setNewCap(sData.monthly_cap || 500);
      }
      if (syncRes.ok) {
        const syData = await syncRes.json();
        setSyncStatus(syData);
      }
      if (dictRes.ok) {
        const dData = await dictRes.json();
        setDictionary(dData.dictionary || []);
      }
    } catch (err) {
      console.error("Failed to load admin stats:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      loadData();
    }
  }, [isOpen]);

  const handleUpdateCap = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch('/api/admin/set-budget-cap', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ monthly_cap: parseFloat(newCap) })
      });
      if (res.ok) {
        setCapMsg("Budget cap updated successfully.");
        loadData();
        setTimeout(() => setCapMsg(''), 3000);
      }
    } catch (err) {
      console.error("Failed to update cap:", err);
    }
  };

  const handleFlushSync = async () => {
    setLoading(true);
    try {
      await fetch('/api/sync/flush', { method: 'POST' });
      await loadData();
    } catch (err) {
      console.error("Sync flush failed:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteDictWord = async (word, lang) => {
    try {
      const res = await fetch('/api/admin/dictionary', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ word, lang })
      });
      if (res.ok) {
        setDictionary(prev => prev.filter(item => !(item.word === word && item.lang === lang)));
      }
    } catch (err) {
      console.error("Failed to delete word:", err);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-md animate-fadeIn">
      <div className="w-full max-w-2xl glass-card rounded-3xl p-6 shadow-2xl border border-white/60 flex flex-col max-h-[85vh] overflow-hidden">
        
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-white/30">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-2xl bg-gradient-to-br from-indigo-500/20 to-purple-500/20 border border-indigo-200/50">
              <Coins className="w-5 h-5 text-indigo-700" />
            </div>
            <div>
              <h2 className="text-base font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
                Cloud & AI Gateway Console
                <span className="text-[10px] bg-emerald-500/15 text-emerald-800 font-extrabold px-2.5 py-0.5 rounded-full border border-emerald-300/40">
                  Cloudflare + Local D1
                </span>
              </h2>
              <p className="text-xs text-slate-500">
                Monthly AI budget caps, SHA-256 savings, Cloudflare sync, and dictionary controls.
              </p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-1.5 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-white/40 transition cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab switcher */}
        <div className="flex gap-2 my-4 p-1 glass-card rounded-2xl">
          <button
            onClick={() => setActiveTab('spend')}
            className={`flex-1 py-1.5 px-3 rounded-xl text-xs font-bold transition flex items-center justify-center gap-1.5 cursor-pointer ${
              activeTab === 'spend' 
                ? 'bg-white shadow-xs text-indigo-700 font-extrabold' 
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <TrendingUp className="w-3.5 h-3.5" /> AI Spend & Cap
          </button>
          <button
            onClick={() => setActiveTab('sync')}
            className={`flex-1 py-1.5 px-3 rounded-xl text-xs font-bold transition flex items-center justify-center gap-1.5 cursor-pointer ${
              activeTab === 'sync' 
                ? 'bg-white shadow-xs text-indigo-700 font-extrabold' 
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Database className="w-3.5 h-3.5" /> Cloudflare D1 Sync
          </button>
          <button
            onClick={() => setActiveTab('dictionary')}
            className={`flex-1 py-1.5 px-3 rounded-xl text-xs font-bold transition flex items-center justify-center gap-1.5 cursor-pointer ${
              activeTab === 'dictionary' 
                ? 'bg-white shadow-xs text-indigo-700 font-extrabold' 
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Shield className="w-3.5 h-3.5" /> School Dictionary ({dictionary.length})
          </button>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto pr-1 flex flex-col gap-4 text-xs">
          {activeTab === 'spend' && stats && (
            <div className="flex flex-col gap-4">
              {/* Spending progress card */}
              <div className="p-4 rounded-2xl bg-gradient-to-br from-indigo-50/70 to-purple-50/60 border border-indigo-100/80">
                <div className="flex justify-between items-center mb-1.5">
                  <span className="font-bold text-slate-700">This Month's AI Expenditure</span>
                  <span className="font-extrabold text-sm text-indigo-900">
                    ₹{stats.monthly_spend.toFixed(2)} / ₹{stats.monthly_cap.toFixed(2)}
                  </span>
                </div>
                {/* Progress bar */}
                <div className="w-full h-3 bg-slate-200/60 rounded-full overflow-hidden border border-slate-300/40">
                  <div 
                    className="h-full bg-gradient-to-r from-indigo-500 to-purple-600 rounded-full transition-all duration-500"
                    style={{ width: `${Math.min(100, stats.cap_percentage)}%` }}
                  />
                </div>
                <div className="flex justify-between text-[11px] text-slate-500 mt-1.5">
                  <span>{stats.cap_percentage}% of budget used</span>
                  <span>{stats.ai_available ? '🟢 AI Features Online' : '🟠 Code-Only Offline Mode'}</span>
                </div>
              </div>

              {/* Metrics Grid */}
              <div className="grid grid-cols-3 gap-3">
                <div className="p-3 rounded-2xl glass-card">
                  <div className="text-[11px] text-slate-500 font-medium">Cache Savings</div>
                  <div className="text-base font-extrabold text-emerald-700 mt-0.5">₹{stats.savings_inr}</div>
                  <div className="text-[10px] text-slate-400">Via SHA-256 local hit</div>
                </div>
                <div className="p-3 rounded-2xl glass-card">
                  <div className="text-[11px] text-slate-500 font-medium">Cache Hit Rate</div>
                  <div className="text-base font-extrabold text-indigo-700 mt-0.5">{stats.cache_hit_rate}%</div>
                  <div className="text-[10px] text-slate-400">{stats.cache_hits} hits / {stats.total_calls} calls</div>
                </div>
                <div className="p-3 rounded-2xl glass-card">
                  <div className="text-[11px] text-slate-500 font-medium">Total AI Tasks</div>
                  <div className="text-base font-extrabold text-purple-700 mt-0.5">{stats.total_calls}</div>
                  <div className="text-[10px] text-slate-400">Batch & cached calls</div>
                </div>
              </div>

              {/* Budget Cap Adjuster Form */}
              <form onSubmit={handleUpdateCap} className="p-3.5 rounded-2xl glass-card flex items-center justify-between">
                <div>
                  <div className="font-bold text-slate-800 flex items-center gap-1.5">
                    <Sliders className="w-3.5 h-3.5 text-indigo-600" /> Monthly Budget Cap (INR)
                  </div>
                  <div className="text-[11px] text-slate-500">Pauses paid AI calls when reached; app stays fully functional offline.</div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="font-bold text-slate-600">₹</span>
                  <input
                    type="number"
                    value={newCap}
                    onChange={(e) => setNewCap(e.target.value)}
                    className="w-20 px-2 py-1 text-center font-bold glass-input rounded-xl text-xs"
                    min="50"
                    step="50"
                  />
                  <button
                    type="submit"
                    className="px-3 py-1.5 rounded-xl font-bold glass-button-primary text-white text-xs cursor-pointer"
                  >
                    Save
                  </button>
                </div>
              </form>
              {capMsg && <p className="text-[11px] text-emerald-700 font-bold">{capMsg}</p>}

              {/* Task Breakdown */}
              <div className="glass-card rounded-2xl p-3.5">
                <div className="font-bold text-slate-800 mb-2">Usage by Task (specs/SOFTWARE-PLAN.md §4)</div>
                <div className="space-y-1.5">
                  {Object.entries(stats.task_stats || {}).map(([task, data]) => (
                    <div key={task} className="flex justify-between items-center py-1 border-b border-slate-100 last:border-none">
                      <span className="font-mono text-slate-600 font-medium">{task}</span>
                      <span className="text-slate-800 font-bold">{data.calls} calls · ₹{data.cost}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'sync' && syncStatus && (
            <div className="flex flex-col gap-4">
              <div className="p-4 rounded-2xl glass-card flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`p-2.5 rounded-2xl ${syncStatus.cloud_connected ? 'bg-emerald-500/20 text-emerald-700' : 'bg-amber-500/20 text-amber-700'}`}>
                    {syncStatus.cloud_connected ? <Cloud className="w-5 h-5" /> : <CloudOff className="w-5 h-5" />}
                  </div>
                  <div>
                    <div className="font-extrabold text-slate-800 text-sm">{syncStatus.mode}</div>
                    <div className="text-[11px] text-slate-500">
                      {syncStatus.cloud_connected 
                        ? 'Connected to Cloudflare Worker D1 & Vectorize' 
                        : 'Offline Mode: Local SQLite Queue active'}
                    </div>
                  </div>
                </div>
                <button
                  onClick={handleFlushSync}
                  disabled={loading}
                  className="px-3 py-2 rounded-xl font-bold glass-button-secondary text-indigo-700 flex items-center gap-1.5 cursor-pointer"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
                  <span>Flush Sync</span>
                </button>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="p-3.5 rounded-2xl glass-card">
                  <span className="text-slate-500 text-[11px]">Pending Sync Items</span>
                  <div className="text-lg font-extrabold text-slate-900 mt-0.5">{syncStatus.pending_sync_items}</div>
                  <div className="text-[10px] text-slate-400">Stored in offline-queue.sqlite</div>
                </div>
                <div className="p-3.5 rounded-2xl glass-card">
                  <span className="text-slate-500 text-[11px]">Last Sync Timestamp</span>
                  <div className="text-xs font-bold text-slate-800 mt-1">{syncStatus.last_sync}</div>
                  <div className="text-[10px] text-slate-400">Nightly automated R2 backup</div>
                </div>
              </div>

              <div className="p-3.5 rounded-2xl bg-slate-50/80 border border-slate-200/60 text-slate-600 leading-relaxed text-[11px]">
                <p className="font-bold text-slate-800 mb-1">Architecture Rules (specs/STORAGE-AND-RAG.md):</p>
                <ul className="list-disc list-inside space-y-1">
                  <li>School PC is not trusted with master data; it keeps an offline queue.</li>
                  <li>Cloudflare D1 is the cloud source of truth for questions and usage history.</li>
                  <li>Cloudflare Vectorize + Workers AI <code className="bg-white px-1 py-0.5 rounded">bge-m3</code> runs duplicate warnings (score &ge; 0.92).</li>
                  <li>Exported Word 2007 papers and diagram scans are backed up to R2.</li>
                </ul>
              </div>
            </div>
          )}

          {activeTab === 'dictionary' && (
            <div className="flex flex-col gap-3">
              <div className="flex justify-between items-center">
                <span className="font-bold text-slate-700">Whitelisted School & Local Terms</span>
                <span className="text-slate-400 text-[11px]">{dictionary.length} words registered</span>
              </div>
              <div className="max-h-[300px] overflow-y-auto space-y-1.5">
                {dictionary.map((entry, idx) => (
                  <div key={idx} className="flex justify-between items-center p-2.5 rounded-xl glass-card hover:bg-white/80 transition">
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] uppercase font-extrabold bg-slate-200/70 text-slate-700 px-1.5 py-0.5 rounded-md">
                        {entry.lang}
                      </span>
                      <span className="font-medium text-slate-900 text-xs">{entry.word}</span>
                    </div>
                    <button
                      onClick={() => handleDeleteDictWord(entry.word, entry.lang)}
                      className="text-slate-400 hover:text-red-600 transition p-1 cursor-pointer"
                      title="Remove from dictionary"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ))}
                {dictionary.length === 0 && (
                  <div className="text-center py-8 text-slate-400 text-xs">
                    No custom dictionary terms yet. Add words during grammar review.
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="pt-3 border-t border-white/30 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl text-xs font-bold glass-button-secondary text-slate-700 cursor-pointer"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
