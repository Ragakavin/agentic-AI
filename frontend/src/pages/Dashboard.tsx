import React, { useState, useEffect } from 'react';
import {
  FileText, CheckCircle2, AlertTriangle, XCircle, ShieldAlert,
  Copy, Clock, ArrowUpRight, RefreshCw
} from 'lucide-react';
import {
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip,
  PieChart, Pie, Cell, BarChart, Bar, CartesianGrid
} from 'recharts';
import { api } from '../services/api';
import { AnalyticsData, InvoiceSummary } from '../types';
import { StatusBadge } from '../components/StatusBadge';

interface DashboardProps {
  onNavigate: (page: string, param?: any) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ onNavigate }) => {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [recentInvoices, setRecentInvoices] = useState<InvoiceSummary[]>([]);
  const [loading, setLoading] = useState(true);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [anData, invs] = await Promise.all([
        api.getAnalytics(),
        api.getInvoices({ limit: 6 } as any)
      ]);
      setAnalytics(anData);
      setRecentInvoices(invs.slice(0, 5));
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  if (loading || !analytics) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 text-emerald-600 animate-spin mx-auto mb-2" />
          <p className="text-xs font-semibold text-slate-500">Loading Agentic Dashboard...</p>
        </div>
      </div>
    );
  }

  const k = analytics.kpis;

  const kpiCards = [
    { title: 'Total Invoices', value: k.total_invoices, icon: FileText, color: 'text-blue-600', bg: 'bg-blue-50', border: 'border-blue-100' },
    { title: 'Auto-Approved', value: k.approved, icon: CheckCircle2, color: 'text-emerald-600', bg: 'bg-emerald-50', border: 'border-emerald-100' },
    { title: 'Pending Review', value: k.pending_review, icon: AlertTriangle, color: 'text-amber-600', bg: 'bg-amber-50', border: 'border-amber-100', highlight: true },
    { title: 'Rejected', value: k.rejected, icon: XCircle, color: 'text-rose-600', bg: 'bg-rose-50', border: 'border-rose-100' },
    { title: 'High-Risk Flagged', value: k.high_risk, icon: ShieldAlert, color: 'text-purple-600', bg: 'bg-purple-50', border: 'border-purple-100' },
    { title: 'Duplicate Detected', value: k.duplicates, icon: Copy, color: 'text-indigo-600', bg: 'bg-indigo-50', border: 'border-indigo-100' },
    { title: 'Avg Agent Latency', value: `${k.avg_processing_time_ms} ms`, icon: Clock, color: 'text-teal-600', bg: 'bg-teal-50', border: 'border-teal-100' },
  ];

  return (
    <div className="space-y-6 animate-fadeIn pb-12">
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-slate-900 to-slate-800 rounded-2xl p-6 text-white shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
              Autonomous AP Agent
            </span>
            <span className="text-xs text-slate-400 font-mono">Observe → Reason → Act</span>
          </div>
          <h1 className="text-xl font-bold tracking-tight text-white m-0">
            Intelligent Invoice Analysis & Processing Dashboard
          </h1>
          <p className="text-xs text-slate-300 mt-1 max-w-2xl leading-relaxed">
            Collaborative 10-agent multi-layered validation, statutory tax checking, purchase order line matching, fraud anomaly scoring, and human-in-the-loop review.
          </p>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <button
            onClick={() => onNavigate('upload')}
            className="px-3.5 py-2 rounded-xl text-xs font-bold bg-brand-500 hover:bg-brand-600 text-white transition-colors shadow-sm flex items-center gap-1.5"
          >
            Upload New Invoice
            <ArrowUpRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* KPI Metric Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
        {kpiCards.map((card, i) => {
          const Icon = card.icon;
          return (
            <div
              key={i}
              className={`p-4 rounded-xl border bg-white shadow-2xs hover:shadow-sm transition-all ${
                card.highlight ? 'ring-2 ring-amber-400/40' : ''
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className={`p-2 rounded-lg ${card.bg}`}>
                  <Icon className={`w-4 h-4 ${card.color}`} />
                </div>
              </div>
              <div className="text-2xl font-extrabold text-slate-900 tracking-tight">
                {card.value}
              </div>
              <div className="text-[11px] font-medium text-slate-500 mt-0.5">
                {card.title}
              </div>
            </div>
          );
        })}
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Processing Trend */}
        <div className="lg:col-span-2 bg-white p-5 rounded-xl border border-slate-200 shadow-2xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-900">Invoice Processing & Approval Trend</h3>
              <p className="text-xs text-slate-500">Volume and automated throughput over recent months</p>
            </div>
            <span className="text-xs font-semibold px-2 py-1 rounded bg-slate-100 text-slate-600">
              FY 2026
            </span>
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={analytics.charts.processing_trend}>
                <defs>
                  <linearGradient id="colorInv" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.2} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorApp" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="month" tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#ffffff', borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '12px' }}
                />
                <Area type="monotone" dataKey="invoices" stroke="#3b82f6" strokeWidth={2} fillOpacity={1} fill="url(#colorInv)" name="Total Invoices" />
                <Area type="monotone" dataKey="approved" stroke="#10b981" strokeWidth={2} fillOpacity={1} fill="url(#colorApp)" name="Approved" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Approval Distribution Donut */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-2xs flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-900">Decision Routing Breakdown</h3>
            <p className="text-xs text-slate-500">Autonomous vs Human review distribution</p>
          </div>

          <div className="h-52 flex items-center justify-center my-2">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={analytics.charts.approval_distribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={80}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {analytics.charts.approval_distribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="space-y-2 border-t border-slate-100 pt-3">
            {analytics.charts.approval_distribution.map((d, i) => (
              <div key={i} className="flex items-center justify-between text-xs">
                <span className="flex items-center gap-2 text-slate-600">
                  <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: d.color }} />
                  {d.name}
                </span>
                <span className="font-bold text-slate-800">{d.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Row 2: Top Vendor Spend & Risk Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Risk Distribution */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-2xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-900">Risk Level Distribution (0-100)</h3>
              <p className="text-xs text-slate-500">Invoices categorized across 4 risk tiers</p>
            </div>
          </div>

          <div className="h-52">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={analytics.charts.risk_distribution}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="level" tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" radius={[6, 6, 0, 0]} name="Invoices">
                  {analytics.charts.risk_distribution.map((entry, idx) => (
                    <Cell key={`bar-${idx}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Vendor Spending Breakdown */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-2xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-900">Top Vendor Disbursements (₹)</h3>
              <p className="text-xs text-slate-500">Highest cumulative invoice amounts processed</p>
            </div>
          </div>

          <div className="h-52">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={analytics.charts.vendor_spending} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f1f5f9" />
                <XAxis type="number" tick={{ fontSize: 10, fill: '#64748b' }} axisLine={false} tickLine={false} />
                <YAxis type="category" dataKey="vendor" tick={{ fontSize: 10, fill: '#64748b' }} width={120} axisLine={false} tickLine={false} />
                <Tooltip formatter={(value: any) => [`₹${Number(value).toLocaleString()}`, 'Amount']} />
                <Bar dataKey="amount" fill="#3b82f6" radius={[0, 6, 6, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Recent Invoices Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-2xs p-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-bold text-slate-900">Recent Invoice Processing Queue</h3>
            <p className="text-xs text-slate-500">Live feed of transactions evaluated by autonomous agents</p>
          </div>
          <button
            onClick={() => onNavigate('invoices')}
            className="text-xs font-semibold text-brand-600 hover:text-brand-700 flex items-center gap-1"
          >
            View all invoices <ArrowUpRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-200 text-slate-500 font-semibold uppercase tracking-wider text-[10px] bg-slate-50/50">
                <th className="py-2.5 px-3">Invoice Ref</th>
                <th className="py-2.5 px-3">Vendor</th>
                <th className="py-2.5 px-3">Amount</th>
                <th className="py-2.5 px-3">Risk Score</th>
                <th className="py-2.5 px-3">AI Confidence</th>
                <th className="py-2.5 px-3">Decision</th>
                <th className="py-2.5 px-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {recentInvoices.map((inv) => (
                <tr
                  key={inv.id}
                  onClick={() => onNavigate('invoice-details', inv.id)}
                  className="hover:bg-slate-50/80 cursor-pointer transition-colors"
                >
                  <td className="py-3 px-3 font-semibold text-slate-900 flex items-center gap-1.5">
                    <FileText className="w-3.5 h-3.5 text-slate-400" />
                    <span>{inv.invoice_number || inv.invoice_id}</span>
                  </td>
                  <td className="py-3 px-3 text-slate-700">{inv.vendor_name || 'N/A'}</td>
                  <td className="py-3 px-3 font-semibold text-slate-900">₹{inv.total_amount.toLocaleString()}</td>
                  <td className="py-3 px-3">
                    <span className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-bold ${
                      inv.risk_score <= 30 ? 'bg-emerald-50 text-emerald-700' : (inv.risk_score <= 70 ? 'bg-amber-50 text-amber-700' : 'bg-rose-50 text-rose-700')
                    }`}>
                      {inv.risk_score.toFixed(0)}/100 ({inv.risk_level})
                    </span>
                  </td>
                  <td className="py-3 px-3 text-slate-600 font-mono text-[11px]">
                    {(inv.overall_confidence * 100).toFixed(0)}%
                  </td>
                  <td className="py-3 px-3">
                    <StatusBadge decision={inv.final_decision || inv.status} size="sm" />
                  </td>
                  <td className="py-3 px-3 text-right">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onNavigate('invoice-details', inv.id);
                      }}
                      className="px-2.5 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 text-[11px] font-medium transition-colors"
                    >
                      Inspect Details
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
