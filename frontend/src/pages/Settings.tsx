import React, { useState, useEffect } from 'react';
import { Save, RefreshCw, Sliders, Cpu, Percent } from 'lucide-react';
import { api } from '../services/api';

export const Settings: React.FC = () => {
  const [settings, setSettings] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [savedMsg, setSavedMsg] = useState(false);

  const loadSettings = async () => {
    setLoading(true);
    try {
      const data = await api.getSettings();
      setSettings(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSettings();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await api.updateSettings(settings);
      setSavedMsg(true);
      setTimeout(() => setSavedMsg(false), 3000);
    } catch (err: any) {
      alert(err.message);
    } finally {
      setSaving(false);
    }
  };

  if (loading || !settings) {
    return (
      <div className="py-24 text-center text-slate-400 text-xs">
        <RefreshCw className="w-6 h-6 animate-spin text-emerald-600 mx-auto mb-2" />
        <span>Loading system settings...</span>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fadeIn pb-16">
      <div>
        <h1 className="text-xl font-bold text-slate-900 tracking-tight">System Configuration & Rules</h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Configure autonomous agent routing thresholds, PO matching tolerances, statutory tax schedules, and LLM providers
        </p>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {/* Routing Thresholds */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-2xs space-y-4">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800 flex items-center gap-2">
            <Sliders className="w-4 h-4 text-brand-600" />
            Confidence-Based Decision Routing Thresholds
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
            <div>
              <label className="font-semibold text-slate-700 block mb-1">
                Auto-Approve Min Confidence (0.0 - 1.0)
              </label>
              <input
                type="number"
                step="0.05"
                min="0.5"
                max="1.0"
                value={settings.confidence_auto_approve_min}
                onChange={(e) => setSettings({ ...settings, confidence_auto_approve_min: parseFloat(e.target.value) })}
                className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg"
              />
              <span className="text-[11px] text-slate-400 mt-0.5 block">Default: 0.90 (90%)</span>
            </div>

            <div>
              <label className="font-semibold text-slate-700 block mb-1">
                Review Min Confidence (0.0 - 1.0)
              </label>
              <input
                type="number"
                step="0.05"
                min="0.3"
                max="0.9"
                value={settings.confidence_review_min}
                onChange={(e) => setSettings({ ...settings, confidence_review_min: parseFloat(e.target.value) })}
                className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg"
              />
              <span className="text-[11px] text-slate-400 mt-0.5 block">Default: 0.60 (60%)</span>
            </div>

            <div>
              <label className="font-semibold text-slate-700 block mb-1">
                Max Risk for Auto-Approval (0 - 100)
              </label>
              <input
                type="number"
                min="0"
                max="50"
                value={settings.risk_auto_approve_max}
                onChange={(e) => setSettings({ ...settings, risk_auto_approve_max: parseFloat(e.target.value) })}
                className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg"
              />
              <span className="text-[11px] text-slate-400 mt-0.5 block">Default: 30</span>
            </div>
          </div>
        </div>

        {/* PO Matching Tolerances & Tax Schedules */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-2xs space-y-4">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800 flex items-center gap-2">
            <Percent className="w-4 h-4 text-blue-600" />
            PO Tolerances & Tax Schedules
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
            <div>
              <label className="font-semibold text-slate-700 block mb-1">
                Quantity Tolerance (%)
              </label>
              <input
                type="number"
                step="0.5"
                min="0"
                max="25"
                value={settings.po_quantity_tolerance_pct}
                onChange={(e) => setSettings({ ...settings, po_quantity_tolerance_pct: parseFloat(e.target.value) })}
                className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg"
              />
              <span className="text-[11px] text-slate-400 mt-0.5 block">Default: 5.0%</span>
            </div>

            <div>
              <label className="font-semibold text-slate-700 block mb-1">
                Unit Price Tolerance (%)
              </label>
              <input
                type="number"
                step="0.5"
                min="0"
                max="20"
                value={settings.po_price_tolerance_pct}
                onChange={(e) => setSettings({ ...settings, po_price_tolerance_pct: parseFloat(e.target.value) })}
                className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg"
              />
              <span className="text-[11px] text-slate-400 mt-0.5 block">Default: 3.0%</span>
            </div>

            <div>
              <label className="font-semibold text-slate-700 block mb-1">
                Standard Statutory Tax Rate (%)
              </label>
              <input
                type="number"
                step="1"
                min="0"
                max="40"
                value={settings.default_tax_rate}
                onChange={(e) => setSettings({ ...settings, default_tax_rate: parseFloat(e.target.value) })}
                className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg"
              />
              <span className="text-[11px] text-slate-400 mt-0.5 block">Default: 18% GST</span>
            </div>
          </div>
        </div>

        {/* LLM Layer Configuration */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-2xs space-y-4">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800 flex items-center gap-2">
            <Cpu className="w-4 h-4 text-purple-600" />
            LLM Orchestration Layer
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
            <div>
              <label className="font-semibold text-slate-700 block mb-1">
                LLM Provider
              </label>
              <select
                value={settings.llm_provider}
                onChange={(e) => setSettings({ ...settings, llm_provider: e.target.value })}
                className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg"
              >
                <option value="mock">Local Deterministic Reasoning (Built-in)</option>
                <option value="ollama">Ollama (Local)</option>
                <option value="openai">OpenAI-Compatible API</option>
              </select>
            </div>

            <div>
              <label className="font-semibold text-slate-700 block mb-1">
                Model Name
              </label>
              <input
                type="text"
                value={settings.llm_model}
                onChange={(e) => setSettings({ ...settings, llm_model: e.target.value })}
                className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg font-mono"
              />
              <span className="text-[11px] text-slate-400 mt-0.5 block">E.g., llama3, mistral, gpt-4o-mini</span>
            </div>

            <div>
              <label className="font-semibold text-slate-700 block mb-1">
                Base URL
              </label>
              <input
                type="text"
                value={settings.llm_base_url}
                onChange={(e) => setSettings({ ...settings, llm_base_url: e.target.value })}
                className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg font-mono"
              />
              <span className="text-[11px] text-slate-400 mt-0.5 block">Default: http://localhost:11434</span>
            </div>
          </div>
        </div>

        {/* Save Bar */}
        <div className="flex items-center justify-between">
          <div className="text-xs text-emerald-600 font-bold">
            {savedMsg && 'Settings updated successfully!'}
          </div>
          <button
            type="submit"
            disabled={saving}
            className="px-5 py-2 rounded-xl bg-brand-600 hover:bg-brand-700 text-white text-xs font-bold shadow-sm transition-colors flex items-center gap-2"
          >
            <Save className="w-4 h-4" />
            <span>{saving ? 'Saving...' : 'Save Configuration'}</span>
          </button>
        </div>
      </form>
    </div>
  );
};
