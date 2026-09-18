import React, { useState, useEffect, useCallback } from 'react';
import {
  FileText, Search, ArrowUpDown, Plus,
  RefreshCw, ChevronRight
} from 'lucide-react';
import { api } from '../services/api';
import { InvoiceSummary } from '../types';
import { StatusBadge } from '../components/StatusBadge';

interface InvoicesProps {
  onNavigate: (page: string, param?: any) => void;
  initialSearch?: string;
}

export const Invoices: React.FC<InvoicesProps> = ({ onNavigate, initialSearch = '' }) => {
  const [invoices, setInvoices] = useState<InvoiceSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState(initialSearch);
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [riskFilter, setRiskFilter] = useState('ALL');
  const [sortBy, setSortBy] = useState<'date' | 'amount' | 'risk'>('date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  const loadInvoices = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.getInvoices({
        status: statusFilter !== 'ALL' ? statusFilter : undefined,
        risk_level: riskFilter !== 'ALL' ? riskFilter : undefined,
        search: search || undefined
      });
      setInvoices(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [statusFilter, riskFilter, search]);

  useEffect(() => {
    loadInvoices();
  }, [loadInvoices]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadInvoices();
  };

  // Sorting
  const sortedInvoices = [...invoices].sort((a, b) => {
    if (sortBy === 'amount') {
      return sortOrder === 'asc' ? a.total_amount - b.total_amount : b.total_amount - a.total_amount;
    }
    if (sortBy === 'risk') {
      return sortOrder === 'asc' ? a.risk_score - b.risk_score : b.risk_score - a.risk_score;
    }
    return sortOrder === 'asc' ? a.id - b.id : b.id - a.id;
  });

  return (
    <div className="space-y-5 animate-fadeIn pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Invoice Repository</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Search, filter, and inspect structured invoices analyzed by the autonomous multi-agent pipeline
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => onNavigate('upload')}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-brand-600 hover:bg-brand-700 text-white text-xs font-semibold shadow-2xs transition-colors"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Upload Invoice</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs flex flex-wrap items-center justify-between gap-3">
        <form onSubmit={handleSearchSubmit} className="relative flex-1 min-w-[220px]">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by invoice number, vendor, or reference..."
            className="w-full pl-9 pr-4 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 text-slate-800"
          />
        </form>

        <div className="flex items-center gap-2 flex-wrap">
          {/* Status Filter */}
          <div className="flex items-center gap-1 text-xs">
            <span className="text-slate-400 font-medium">Status:</span>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs font-medium text-slate-700 focus:outline-none"
            >
              <option value="ALL">All Statuses</option>
              <option value="approved">Approved</option>
              <option value="review_required">Review Required</option>
              <option value="rejected">Rejected</option>
            </select>
          </div>

          {/* Risk Filter */}
          <div className="flex items-center gap-1 text-xs">
            <span className="text-slate-400 font-medium">Risk:</span>
            <select
              value={riskFilter}
              onChange={(e) => setRiskFilter(e.target.value)}
              className="px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs font-medium text-slate-700 focus:outline-none"
            >
              <option value="ALL">All Risk Levels</option>
              <option value="LOW">Low Risk</option>
              <option value="MEDIUM">Medium Risk</option>
              <option value="HIGH">High Risk</option>
              <option value="CRITICAL">Critical Risk</option>
            </select>
          </div>

          {/* Sort Control */}
          <div className="flex items-center gap-1 text-xs">
            <span className="text-slate-400 font-medium">Sort:</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as 'date' | 'amount' | 'risk')}
              className="px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs font-medium text-slate-700 focus:outline-none"
            >
              <option value="date">Date</option>
              <option value="amount">Amount</option>
              <option value="risk">Risk Score</option>
            </select>
          </div>
          <button
            onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
            className="p-1.5 rounded-lg border border-slate-200 bg-slate-50 hover:bg-slate-100 text-slate-600 transition-colors"
            title="Toggle sort direction"
          >
            <ArrowUpDown className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Main Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-2xs overflow-hidden">
        {loading ? (
          <div className="py-20 text-center text-slate-400 text-xs flex flex-col items-center gap-2">
            <RefreshCw className="w-6 h-6 animate-spin text-emerald-600" />
            <span>Loading invoice records...</span>
          </div>
        ) : sortedInvoices.length === 0 ? (
          <div className="py-20 text-center text-slate-400 text-xs">
            No invoices found matching current filter criteria.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-200 text-slate-500 font-semibold uppercase tracking-wider text-[10px] bg-slate-50/70">
                  <th className="py-3 px-4">Invoice #</th>
                  <th className="py-3 px-4">Vendor</th>
                  <th className="py-3 px-4">Date</th>
                  <th className="py-3 px-4">Total (₹)</th>
                  <th className="py-3 px-4">Risk Level</th>
                  <th className="py-3 px-4">AI Confidence</th>
                  <th className="py-3 px-4">Decision Status</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {sortedInvoices.map((inv) => (
                  <tr
                    key={inv.id}
                    onClick={() => onNavigate('invoice-details', inv.id)}
                    className="hover:bg-slate-50/80 cursor-pointer transition-colors"
                  >
                    <td className="py-3 px-4 font-bold text-slate-900 flex items-center gap-2">
                      <FileText className="w-4 h-4 text-slate-400 shrink-0" />
                      <div>
                        <span>{inv.invoice_number || inv.invoice_id}</span>
                        <div className="text-[10px] text-slate-400 font-mono">{inv.invoice_id}</div>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-slate-800 font-medium">{inv.vendor_name || 'N/A'}</td>
                    <td className="py-3 px-4 text-slate-500 font-mono text-[11px]">{inv.invoice_date || 'N/A'}</td>
                    <td className="py-3 px-4 font-bold text-slate-900">
                      ₹{inv.total_amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </td>
                    <td className="py-3 px-4">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-bold ${
                        inv.risk_score <= 30
                          ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                          : (inv.risk_score <= 70
                            ? 'bg-amber-50 text-amber-700 border border-amber-200'
                            : 'bg-rose-50 text-rose-700 border border-rose-200')
                      }`}>
                        {inv.risk_score.toFixed(0)}/100 ({inv.risk_level})
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-600 font-mono text-[11px]">
                      {(inv.overall_confidence * 100).toFixed(0)}%
                    </td>
                    <td className="py-3 px-4">
                      <StatusBadge decision={inv.final_decision || inv.status} size="sm" />
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onNavigate('invoice-details', inv.id);
                        }}
                        className="px-2.5 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 text-[11px] font-medium transition-colors inline-flex items-center gap-1"
                      >
                        Inspect <ChevronRight className="w-3 h-3" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="p-3 border-t border-slate-100 bg-slate-50/50 flex items-center justify-between text-xs text-slate-500">
          <span>Showing {sortedInvoices.length} transactions</span>
          <div className="flex items-center gap-1">
            <span className="font-semibold text-slate-700">Autonomous AP Guard</span>
          </div>
        </div>
      </div>
    </div>
  );
};
