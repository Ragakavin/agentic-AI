import React, { useState, useEffect } from 'react';
import {
  CheckSquare, AlertTriangle, CheckCircle2, XCircle, FileText,
  RefreshCw, MessageSquare, ArrowRight, ShieldAlert, Sparkles
} from 'lucide-react';
import { api } from '../services/api';
import { InvoiceSummary } from '../types';
import { StatusBadge } from '../components/StatusBadge';

interface ReviewQueueProps {
  onNavigate: (page: string, param?: any) => void;
}

export const ReviewQueue: React.FC<ReviewQueueProps> = ({ onNavigate }) => {
  const [invoices, setInvoices] = useState<InvoiceSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedInvoice, setSelectedInvoice] = useState<InvoiceSummary | null>(null);
  const [comment, setComment] = useState('');
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    loadReviewQueue();
  }, []);

  const loadReviewQueue = async () => {
    setLoading(true);
    try {
      const data = await api.getInvoices({ status: 'review_required' });
      setInvoices(data);
      if (data.length > 0 && !selectedInvoice) {
        setSelectedInvoice(data[0]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (decision: 'APPROVE' | 'REJECT') => {
    if (!selectedInvoice) return;
    setActionLoading(true);
    try {
      await api.reviewInvoice(selectedInvoice.id, decision, comment);
      setComment('');
      await loadReviewQueue();
      alert(`Invoice ${selectedInvoice.invoice_number || selectedInvoice.invoice_id} resolved as ${decision}. Context stored in system long-term memory.`);
    } catch (err: any) {
      alert(err.message);
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn pb-16">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2">
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">
            Human-in-the-Loop Review Station
          </h1>
          <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-amber-50 text-amber-700 border border-amber-200">
            {invoices.length} Pending
          </span>
        </div>
        <p className="text-xs text-slate-500 mt-0.5">
          Review discrepancies flagged by the autonomous agent matrix. Your overrides and justification comments feed the long-term memory.
        </p>
      </div>

      {loading ? (
        <div className="py-20 text-center text-slate-400 text-xs">
          <RefreshCw className="w-6 h-6 animate-spin text-amber-600 mx-auto mb-2" />
          <span>Loading pending review items...</span>
        </div>
      ) : invoices.length === 0 ? (
        <div className="bg-white p-12 rounded-2xl border border-slate-200 text-center space-y-3">
          <div className="w-12 h-12 rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center mx-auto">
            <CheckCircle2 className="w-6 h-6" />
          </div>
          <h3 className="text-sm font-bold text-slate-900">Review Queue Cleared</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            All current invoices have been processed and either auto-approved or reviewed.
          </p>
          <button
            onClick={() => onNavigate('upload')}
            className="px-3.5 py-1.5 rounded-lg bg-slate-900 text-white text-xs font-semibold"
          >
            Upload Next Invoice
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Left: Queue List */}
          <div className="lg:col-span-5 bg-white rounded-2xl border border-slate-200 shadow-2xs overflow-hidden">
            <div className="p-3.5 border-b border-slate-100 bg-slate-50/70 text-xs font-bold text-slate-700 uppercase tracking-wider">
              Awaiting Financial Review
            </div>
            <div className="divide-y divide-slate-100 max-h-[600px] overflow-y-auto">
              {invoices.map((inv) => (
                <div
                  key={inv.id}
                  onClick={() => setSelectedInvoice(inv)}
                  className={`p-4 cursor-pointer transition-colors ${
                    selectedInvoice?.id === inv.id ? 'bg-amber-50/50 border-l-4 border-amber-500' : 'hover:bg-slate-50'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-bold text-slate-900">
                      {inv.invoice_number || inv.invoice_id}
                    </span>
                    <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-rose-50 text-rose-700 border border-rose-200">
                      Risk {inv.risk_score.toFixed(0)}/100
                    </span>
                  </div>
                  <div className="text-xs text-slate-600 font-medium">
                    {inv.vendor_name || 'Vendor N/A'}
                  </div>
                  <div className="flex items-center justify-between mt-2 text-[11px] text-slate-500">
                    <span className="font-bold text-slate-800">₹{inv.total_amount.toLocaleString()}</span>
                    <span>Date: {inv.invoice_date || 'N/A'}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Right: Quick Action Review Panel */}
          {selectedInvoice && (
            <div className="lg:col-span-7 bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-5">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <div>
                  <h3 className="text-sm font-bold text-slate-900">
                    Review Target: {selectedInvoice.invoice_number || selectedInvoice.invoice_id}
                  </h3>
                  <p className="text-xs text-slate-500 mt-0.5">
                    {selectedInvoice.vendor_name} • Total ₹{selectedInvoice.total_amount.toLocaleString()}
                  </p>
                </div>
                <button
                  onClick={() => onNavigate('invoice-details', selectedInvoice.id)}
                  className="text-xs font-semibold text-brand-600 hover:text-brand-700 flex items-center gap-1"
                >
                  Full Details <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>

              {/* Anomaly Guidance Note */}
              <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 text-xs text-amber-900 space-y-1.5">
                <div className="font-bold flex items-center gap-1.5">
                  <AlertTriangle className="w-4 h-4 text-amber-600" />
                  Primary Discrepancy & AI Findings
                </div>
                <p className="leading-relaxed">
                  {selectedInvoice.ai_recommendation}: Evaluated at <strong>{selectedInvoice.risk_score.toFixed(0)}/100 risk score</strong>.
                  Exceeds automatic approval bounds. Human verification required before release.
                </p>
              </div>

              {/* Reviewer Comment Field */}
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-700 flex items-center gap-1.5">
                  <MessageSquare className="w-3.5 h-3.5 text-slate-500" />
                  Reviewer Decision Justification:
                </label>
                <textarea
                  rows={4}
                  value={comment}
                  onChange={(e) => setComment(e.target.value)}
                  placeholder="State the rationale for approving or rejecting (e.g., 'Vendor confirmed PO overrun allowance under Contract Amendment #4')..."
                  className="w-full p-3 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500/20 text-slate-800"
                />
                <span className="text-[11px] text-slate-400">
                  Tip: This comment will be permanently associated with the vendor's behavioral profile in Long-Term Memory.
                </span>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center gap-3 pt-2">
                <button
                  onClick={() => handleAction('APPROVE')}
                  disabled={actionLoading}
                  className="flex-1 py-2.5 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-sm transition-colors flex items-center justify-center gap-2"
                >
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Authorize & Approve Payment</span>
                </button>

                <button
                  onClick={() => handleAction('REJECT')}
                  disabled={actionLoading}
                  className="flex-1 py-2.5 px-4 rounded-xl bg-rose-600 hover:bg-rose-700 text-white font-bold text-xs shadow-sm transition-colors flex items-center justify-center gap-2"
                >
                  <XCircle className="w-4 h-4" />
                  <span>Reject Transaction</span>
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
