import React, { useState, useEffect } from 'react';
import { RefreshCw } from 'lucide-react';
import {
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip,
  BarChart, Bar, CartesianGrid
} from 'recharts';
import { api } from '../services/api';
import { AnalyticsData } from '../types';

export const Analytics: React.FC = () => {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      const data = await api.getAnalytics();
      setAnalytics(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading || !analytics) {
    return (
      <div className="py-24 text-center text-slate-400 text-xs">
        <RefreshCw className="w-6 h-6 animate-spin text-emerald-600 mx-auto mb-2" />
        <span>Loading in-depth analytics...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fadeIn pb-16">
      <div>
        <h1 className="text-xl font-bold text-slate-900 tracking-tight">Financial & Compliance Analytics</h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Macro AP performance metrics, anomaly exposure rates, and automated decision accuracy
        </p>
      </div>

      {/* Row 1: High Level Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="p-4 bg-white rounded-xl border border-slate-200 shadow-2xs">
          <span className="text-[11px] text-slate-500 font-medium">Auto-Approval Rate</span>
          <div className="text-2xl font-extrabold text-emerald-600 tracking-tight mt-1">
            {analytics.kpis.total_invoices ? ((analytics.kpis.approved / analytics.kpis.total_invoices) * 100).toFixed(1) : 0}%
          </div>
          <span className="text-[10px] text-slate-400">Zero human intervention</span>
        </div>

        <div className="p-4 bg-white rounded-xl border border-slate-200 shadow-2xs">
          <span className="text-[11px] text-slate-500 font-medium">Human Review Rate</span>
          <div className="text-2xl font-extrabold text-amber-600 tracking-tight mt-1">
            {analytics.kpis.total_invoices ? ((analytics.kpis.pending_review / analytics.kpis.total_invoices) * 100).toFixed(1) : 0}%
          </div>
          <span className="text-[10px] text-slate-400">Flagged by anomaly rules</span>
        </div>

        <div className="p-4 bg-white rounded-xl border border-slate-200 shadow-2xs">
          <span className="text-[11px] text-slate-500 font-medium">Avg Processing Turnaround</span>
          <div className="text-2xl font-extrabold text-blue-600 tracking-tight mt-1 font-mono">
            {analytics.kpis.avg_processing_time_ms} ms
          </div>
          <span className="text-[10px] text-slate-400">From upload to final decision</span>
        </div>

        <div className="p-4 bg-white rounded-xl border border-slate-200 shadow-2xs">
          <span className="text-[11px] text-slate-500 font-medium">Critical Risk Invoices</span>
          <div className="text-2xl font-extrabold text-rose-600 tracking-tight mt-1">
            {analytics.kpis.high_risk}
          </div>
          <span className="text-[10px] text-slate-400">Severe discrepancy / duplicate</span>
        </div>
      </div>

      {/* Row 2: Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Processing Volume Trend */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-2xs">
          <h3 className="text-sm font-bold text-slate-900 mb-1">Monthly Transaction Value (₹)</h3>
          <p className="text-xs text-slate-500 mb-4">Total capital processed through agentic workflows</p>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={analytics.charts.processing_trend}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="month" tick={{ fontSize: 10, fill: '#64748b' }} />
                <YAxis tick={{ fontSize: 10, fill: '#64748b' }} tickFormatter={(val) => `₹${val/1000}k`} />
                <Tooltip formatter={(val: any) => [`₹${Number(val).toLocaleString()}`, 'Amount']} />
                <Area type="monotone" dataKey="amount" stroke="#10b981" fill="#10b981" fillOpacity={0.2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* AI Extraction Confidence Distribution */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-2xs">
          <h3 className="text-sm font-bold text-slate-900 mb-1">AI Extraction Confidence Distribution</h3>
          <p className="text-xs text-slate-500 mb-4">Reliability spread across header and item extractions</p>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={analytics.charts.confidence_distribution}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="bucket" tick={{ fontSize: 10, fill: '#64748b' }} />
                <YAxis tick={{ fontSize: 10, fill: '#64748b' }} allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#3b82f6" radius={[6, 6, 0, 0]} name="Invoices" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
