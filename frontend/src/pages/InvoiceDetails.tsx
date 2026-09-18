import React, { useState, useEffect, useCallback } from 'react';
import {
  FileText, ArrowLeft, CheckCircle2, AlertTriangle, XCircle,
  RefreshCw, Download, FileSpreadsheet, ShieldAlert, BrainCircuit,
  ShoppingCart, Calculator
} from 'lucide-react';
import { api } from '../services/api';
import { InvoiceDetail } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { RiskGauge } from '../components/RiskGauge';
import { AgentPipelineVisualizer } from '../components/AgentPipelineVisualizer';

interface InvoiceDetailsProps {
  invoiceId: number;
  onNavigate: (page: string, param?: any) => void;
}

export const InvoiceDetails: React.FC<InvoiceDetailsProps> = ({ invoiceId, onNavigate }) => {
  const [invoice, setInvoice] = useState<InvoiceDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'reasoning' | 'extracted' | 'validation' | 'po' | 'fraud' | 'timeline' | 'review'>('reasoning');
  const [isReanalyzing, setIsReanalyzing] = useState(false);
  const [reviewComment, setReviewComment] = useState('');
  const [reviewSubmitting, setReviewSubmitting] = useState(false);
  const [reportGenerating, setReportGenerating] = useState<string | null>(null);

  const loadDetail = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.getInvoiceDetail(invoiceId);
      setInvoice(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [invoiceId]);

  useEffect(() => {
    loadDetail();
  }, [loadDetail]);

  const handleReanalyze = async () => {
    setIsReanalyzing(true);
    try {
      await api.reanalyzeInvoice(invoiceId);
      await loadDetail();
    } catch (err: any) {
      alert(err.message);
    } finally {
      setIsReanalyzing(false);
    }
  };

  const handleReviewAction = async (decision: 'APPROVE' | 'REJECT') => {
    setReviewSubmitting(true);
    try {
      await api.reviewInvoice(invoiceId, decision, reviewComment);
      await loadDetail();
      alert(`Invoice marked as ${decision}. Human feedback recorded in long-term memory.`);
    } catch (err: any) {
      alert(err.message);
    } finally {
      setReviewSubmitting(false);
    }
  };

  const handleExportReport = async (format: 'PDF' | 'EXCEL' | 'CSV') => {
    setReportGenerating(format);
    try {
      const res = await api.generateReport(invoiceId, format);
      window.open(res.download_url, '_blank');
    } catch (err: any) {
      alert(err.message);
    } finally {
      setReportGenerating(null);
    }
  };

  if (loading || !invoice) {
    return (
      <div className="py-24 text-center">
        <RefreshCw className="w-8 h-8 text-emerald-600 animate-spin mx-auto mb-2" />
        <p className="text-xs font-semibold text-slate-500">Loading comprehensive invoice analysis...</p>
      </div>
    );
  }

  const val = invoice.validations;
  const risk = invoice.risk_assessment;

  return (
    <div className="space-y-6 animate-fadeIn pb-16">
      {/* Top Breadcrumb & Action Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs">
        <div className="flex items-center gap-3">
          <button
            onClick={() => onNavigate('invoices')}
            className="p-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-600 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-bold text-slate-900 tracking-tight">
                {invoice.invoice_number || invoice.invoice_id}
              </h1>
              <StatusBadge decision={invoice.final_decision || invoice.status} size="md" />
              <span className="text-xs text-slate-400 font-mono">({invoice.invoice_id})</span>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              {invoice.vendor_name_extracted} • Uploaded {invoice.created_at ? new Date(invoice.created_at).toLocaleString() : 'Recently'}
            </p>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2 flex-wrap">
          <button
            onClick={handleReanalyze}
            disabled={isReanalyzing}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 bg-slate-50 hover:bg-slate-100 text-xs font-semibold text-slate-700 transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isReanalyzing ? 'animate-spin text-emerald-600' : ''}`} />
            <span>Re-Analyze</span>
          </button>

          {/* Export Dropdown / Buttons */}
          <button
            onClick={() => handleExportReport('PDF')}
            disabled={reportGenerating === 'PDF'}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 bg-slate-50 hover:bg-slate-100 text-xs font-semibold text-slate-700 transition-colors"
          >
            <Download className="w-3.5 h-3.5 text-blue-600" />
            <span>PDF Report</span>
          </button>

          <button
            onClick={() => handleExportReport('EXCEL')}
            disabled={reportGenerating === 'EXCEL'}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 bg-slate-50 hover:bg-slate-100 text-xs font-semibold text-slate-700 transition-colors"
          >
            <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-600" />
            <span>Excel</span>
          </button>

          {invoice.status === 'review_required' && (
            <button
              onClick={() => setActiveTab('review')}
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-600 text-white text-xs font-bold shadow-2xs transition-colors"
            >
              <AlertTriangle className="w-3.5 h-3.5" />
              <span>Review Needed</span>
            </button>
          )}
        </div>
      </div>

      {/* 10-Agent Collaborative Autonomous Pipeline Trace */}
      <AgentPipelineVisualizer runs={invoice.agent_runs} isProcessing={isReanalyzing} />

      {/* Main Split Layout: Left Simulated Document Viewer | Right Deep Agent Analysis Panels */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Simulated Original Invoice Document (5 cols) */}
        <div className="lg:col-span-5 bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-6">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4 text-slate-400" />
              <span className="text-xs font-bold uppercase tracking-wider text-slate-700">
                Original Document View
              </span>
            </div>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-100 text-slate-600">
              {invoice.file_type} • {invoice.original_filename}
            </span>
          </div>

          {/* Rendered Invoice Paper Layout */}
          <div className="p-6 bg-slate-50/70 border border-slate-200 rounded-xl text-slate-800 text-xs space-y-5 shadow-2xs font-sans">
            {/* Header Block */}
            <div className="flex justify-between items-start">
              <div>
                <h2 className="text-base font-extrabold text-slate-900 tracking-tight">
                  {invoice.vendor_name_extracted}
                </h2>
                <p className="text-[11px] text-slate-500 max-w-[220px] mt-0.5">
                  {invoice.vendor_address_extracted || 'Commercial Business Park, Sector 4'}
                </p>
                <p className="text-[11px] text-slate-500">{invoice.vendor_email_extracted}</p>
                <p className="text-[11px] font-mono text-slate-600 mt-1">
                  GSTIN: {invoice.vendor_tax_id_extracted || '29AABCA1234F1Z8'}
                </p>
              </div>

              <div className="text-right">
                <div className="text-sm font-bold text-slate-900 font-mono">{invoice.invoice_number}</div>
                <div className="text-[11px] text-slate-500 mt-1">Date: {invoice.invoice_date}</div>
                <div className="text-[11px] text-slate-500">Due: {invoice.due_date || 'Net 30'}</div>
                <div className="text-[11px] font-medium text-blue-700 mt-1">
                  PO: {invoice.purchase_order?.po_number || (invoice.extracted_fields as any)?.po_number?.value || 'N/A'}
                </div>
              </div>
            </div>

            {/* Line Items Table */}
            <div className="border border-slate-200 rounded-lg overflow-hidden bg-white">
              <table className="w-full text-left text-[11px]">
                <thead className="bg-slate-100 text-slate-600 font-semibold uppercase text-[10px]">
                  <tr>
                    <th className="p-2">Item Description</th>
                    <th className="p-2 text-right">Qty</th>
                    <th className="p-2 text-right">Unit Price</th>
                    <th className="p-2 text-right">Total</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {invoice.items.map((it, idx) => (
                    <tr key={idx} className="hover:bg-slate-50">
                      <td className="p-2 font-medium text-slate-800">{it.description}</td>
                      <td className="p-2 text-right font-mono">{it.quantity}</td>
                      <td className="p-2 text-right font-mono">₹{it.unit_price.toLocaleString()}</td>
                      <td className="p-2 text-right font-bold font-mono">₹{it.total_price.toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Financial Summary */}
            <div className="flex justify-end pt-2">
              <div className="w-56 space-y-1.5 text-xs">
                <div className="flex justify-between text-slate-600">
                  <span>Subtotal:</span>
                  <span className="font-mono">₹{invoice.subtotal.toLocaleString(undefined, { minimumFractionDigits: 2 })}</span>
                </div>
                <div className="flex justify-between text-slate-600">
                  <span>Tax ({invoice.tax_percentage || 18}%):</span>
                  <span className="font-mono">₹{invoice.tax_amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}</span>
                </div>
                <div className="flex justify-between text-sm font-bold text-slate-900 border-t border-slate-200 pt-1.5">
                  <span>Grand Total:</span>
                  <span className="font-mono text-emerald-700">₹{invoice.total_amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}</span>
                </div>
              </div>
            </div>

            {/* Bank Details */}
            <div className="border-t border-slate-200 pt-3 flex justify-between text-[11px] text-slate-500">
              <div>
                <span className="font-semibold text-slate-700 block">Bank Account:</span>
                <span className="font-mono">{invoice.bank_account_extracted || 'N/A'}</span>
              </div>
              <div className="text-right">
                <span className="font-semibold text-slate-700 block">IFSC Code:</span>
                <span className="font-mono">{invoice.bank_ifsc_extracted || 'N/A'}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Multi-Agent Analysis & Decision Center (7 cols) */}
        <div className="lg:col-span-7 bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-5">
          {/* Risk Gauge and AI Decision Summary Bar */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <RiskGauge score={invoice.risk_score} level={invoice.risk_level} />

            <div className="p-4 rounded-xl border border-slate-200 bg-slate-50/80 flex flex-col justify-between">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 block mb-1">
                  Autonomous Decision
                </span>
                <div className="flex items-center gap-2 mb-2">
                  <StatusBadge decision={invoice.final_decision || invoice.status} size="lg" />
                </div>
                <p className="text-xs text-slate-600 leading-relaxed">
                  {invoice.recommended_action || 'Processed through standard multi-agent pipeline.'}
                </p>
              </div>

              <div className="flex items-center justify-between border-t border-slate-200/80 pt-2 mt-2 text-[11px] text-slate-500">
                <span>AI Confidence: <strong className="text-slate-800 font-mono">{(invoice.overall_confidence * 100).toFixed(0)}%</strong></span>
                <span>Latency: <strong className="text-slate-800 font-mono">{invoice.processing_time_ms} ms</strong></span>
              </div>
            </div>
          </div>

          {/* Analysis Tabs */}
          <div className="border-b border-slate-200 flex items-center gap-2 overflow-x-auto text-xs">
            {[
              { id: 'reasoning', label: 'AI Reasoning', icon: BrainCircuit },
              { id: 'extracted', label: 'Extracted Fields', icon: FileText },
              { id: 'validation', label: 'Math & Tax', icon: Calculator },
              { id: 'po', label: 'PO Matching', icon: ShoppingCart },
              { id: 'fraud', label: 'Fraud Matrix', icon: ShieldAlert },
              { id: 'review', label: 'Review Action', icon: CheckCircle2 },
            ].map(tab => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`py-2.5 px-3 border-b-2 font-semibold flex items-center gap-1.5 transition-colors whitespace-nowrap ${
                    isActive
                      ? 'border-brand-600 text-brand-700 bg-brand-50/40 rounded-t-lg'
                      : 'border-transparent text-slate-500 hover:text-slate-800'
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  {tab.label}
                </button>
              );
            })}
          </div>

          {/* Tab 1: AI Reasoning & Grounded Evidence */}
          {activeTab === 'reasoning' && (
            <div className="space-y-4 animate-fadeIn">
              <div>
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-2">
                  Evidence Synthesized From Specialized Agents
                </h3>
                <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-800 space-y-2 leading-relaxed">
                  {invoice.decision_reasons && invoice.decision_reasons.length > 0 ? (
                    invoice.decision_reasons.map((r, i) => (
                      <div key={i} className="flex items-start gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-blue-600 mt-1.5 shrink-0" />
                        <span>{r}</span>
                      </div>
                    ))
                  ) : (
                    <div className="flex items-center gap-2 text-emerald-700">
                      <CheckCircle2 className="w-4 h-4" />
                      <span>All automated compliance, mathematical checks, and PO comparisons verified cleanly.</span>
                    </div>
                  )}
                </div>
              </div>

              <div>
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-2">
                  Recommended Action
                </h3>
                <div className="p-3.5 rounded-xl bg-blue-50/80 border border-blue-200 text-xs text-blue-900 font-medium">
                  {invoice.recommended_action || 'Proceed with payment clearance.'}
                </div>
              </div>
            </div>
          )}

          {/* Tab 2: Extracted Fields with Per-Field Confidence */}
          {activeTab === 'extracted' && (
            <div className="space-y-3 animate-fadeIn">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">
                Layout Extracted Key-Value Elements & Confidence Scores
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 max-h-96 overflow-y-auto pr-1">
                {invoice.extracted_fields &&
                  Object.entries(invoice.extracted_fields).map(([key, valObj]: [string, any]) => {
                    if (key === 'line_items' || typeof valObj !== 'object' || !valObj) return null;
                    return (
                      <div key={key} className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-xs">
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-semibold text-slate-600 capitalize">
                            {key.replace(/_/g, ' ')}
                          </span>
                          <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-white text-emerald-700 font-bold border border-slate-200">
                            {valObj.confidence ? `${(valObj.confidence * 100).toFixed(0)}%` : '95%'}
                          </span>
                        </div>
                        <div className="font-bold text-slate-900 truncate">
                          {String(valObj.value ?? 'N/A')}
                        </div>
                        {valObj.location && (
                          <div className="text-[10px] text-slate-400 mt-1 italic truncate">
                            Source: {valObj.location}
                          </div>
                        )}
                      </div>
                    );
                  })}
              </div>
            </div>
          )}

          {/* Tab 3: Itemized Math & Tax Check */}
          {activeTab === 'validation' && val && (
            <div className="space-y-4 animate-fadeIn text-xs">
              <div className="p-4 rounded-xl border border-slate-200 bg-slate-50 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-slate-800">Mathematical Calculation Verification</span>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    val.math_status === 'PASS' ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'
                  }`}>
                    {val.math_status}
                  </span>
                </div>
                <div className="grid grid-cols-3 gap-2 text-center">
                  <div className="p-2 bg-white rounded border border-slate-200">
                    <span className="text-[10px] text-slate-500 block">Calculated Total</span>
                    <span className="font-bold font-mono">₹{val.calculated_total.toLocaleString()}</span>
                  </div>
                  <div className="p-2 bg-white rounded border border-slate-200">
                    <span className="text-[10px] text-slate-500 block">Invoice Total</span>
                    <span className="font-bold font-mono">₹{val.invoice_total.toLocaleString()}</span>
                  </div>
                  <div className="p-2 bg-white rounded border border-slate-200">
                    <span className="text-[10px] text-slate-500 block">Difference</span>
                    <span className="font-bold font-mono text-emerald-700">₹{val.math_difference}</span>
                  </div>
                </div>
                <p className="text-[11px] text-slate-600">{val.math_notes}</p>
              </div>

              <div className="p-4 rounded-xl border border-slate-200 bg-slate-50 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-slate-800">Statutory Tax Schedule Check</span>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    val.tax_status === 'PASS' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
                  }`}>
                    {val.tax_status}
                  </span>
                </div>
                <div className="grid grid-cols-3 gap-2 text-center">
                  <div className="p-2 bg-white rounded border border-slate-200">
                    <span className="text-[10px] text-slate-500 block">Expected Rate</span>
                    <span className="font-bold font-mono">{val.expected_tax_rate}%</span>
                  </div>
                  <div className="p-2 bg-white rounded border border-slate-200">
                    <span className="text-[10px] text-slate-500 block">Detected Rate</span>
                    <span className="font-bold font-mono">{val.detected_tax_rate}%</span>
                  </div>
                  <div className="p-2 bg-white rounded border border-slate-200">
                    <span className="text-[10px] text-slate-500 block">Tax Variance</span>
                    <span className="font-bold font-mono text-amber-700">₹{val.tax_difference.toLocaleString()}</span>
                  </div>
                </div>
                <p className="text-[11px] text-slate-600">{val.tax_notes}</p>
              </div>
            </div>
          )}

          {/* Tab 4: Purchase Order Matching */}
          {activeTab === 'po' && val && (
            <div className="space-y-4 animate-fadeIn text-xs">
              <div className="p-4 rounded-xl border border-slate-200 bg-slate-50 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-slate-800">
                    PO Match: {val.po_number || 'None'}
                  </span>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    val.po_match_status === 'PASS' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
                  }`}>
                    {val.po_match_status}
                  </span>
                </div>

                {val.po_discrepancies && val.po_discrepancies.length > 0 ? (
                  <div className="space-y-1.5">
                    <span className="font-semibold text-rose-700 block">Discrepancies Flagged:</span>
                    {val.po_discrepancies.map((disc, idx) => (
                      <div key={idx} className="p-2 bg-rose-50 border border-rose-200 rounded text-rose-800">
                        {disc}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-emerald-700 font-medium">
                    All invoice line items, quantities, and unit prices match the Purchase Order within configured tolerance bounds (5% Qty, 3% Price).
                  </p>
                )}
              </div>
            </div>
          )}

          {/* Tab 5: Fraud & Anomaly Matrix */}
          {activeTab === 'fraud' && risk && (
            <div className="space-y-3 animate-fadeIn text-xs">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">
                12-Point Anomaly & Fraud Assessment Results
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-h-96 overflow-y-auto">
                {[
                  { key: 'duplicate_risk', label: 'Duplicate Invoice Check', val: risk.duplicate_risk },
                  { key: 'unusual_amount_risk', label: 'Unusual Amount Deviation', val: risk.unusual_amount_risk },
                  { key: 'unusual_tax_risk', label: 'Tax Schedule Variance', val: risk.unusual_tax_risk },
                  { key: 'repeat_invoice_num_risk', label: 'Repeated Invoice Number', val: risk.repeat_invoice_num_risk },
                  { key: 'vendor_mismatch_risk', label: 'Vendor Master Mismatch', val: risk.vendor_mismatch_risk },
                  { key: 'suspicious_bank_risk', label: 'Bank Account Discrepancy', val: risk.suspicious_bank_risk },
                  { key: 'abnormal_quantity_risk', label: 'Abnormal Quantity Check', val: risk.abnormal_quantity_risk },
                  { key: 'price_anomaly_risk', label: 'Price Anomaly Check', val: risk.price_anomaly_risk },
                  { key: 'weekend_pattern_risk', label: 'Weekend / Off-Hours Pattern', val: risk.weekend_pattern_risk },
                  { key: 'unusual_frequency_risk', label: 'Unusual Frequency Check', val: risk.unusual_frequency_risk },
                  { key: 'modified_pattern_risk', label: 'Math Pattern Alteration', val: risk.modified_pattern_risk },
                  { key: 'missing_info_risk', label: 'Mandatory Information Check', val: risk.missing_info_risk },
                ].map(item => (
                  <div
                    key={item.key}
                    className={`p-2.5 rounded-lg border flex items-center justify-between ${
                      item.val ? 'bg-rose-50/70 border-rose-200 text-rose-800' : 'bg-slate-50 border-slate-200 text-slate-700'
                    }`}
                  >
                    <span>{item.label}</span>
                    <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                      item.val ? 'bg-rose-200 text-rose-900' : 'bg-emerald-100 text-emerald-800'
                    }`}>
                      {item.val ? 'FLAGGED' : 'PASSED'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Tab 6: Human-in-the-Loop Review Form */}
          {activeTab === 'review' && (
            <div className="space-y-4 animate-fadeIn text-xs">
              <div className="p-4 rounded-xl bg-amber-50/60 border border-amber-200 space-y-2">
                <span className="font-bold text-amber-900 flex items-center gap-1.5">
                  <AlertTriangle className="w-4 h-4 text-amber-600" />
                  Human Review & Decision Override Station
                </span>
                <p className="text-slate-600">
                  You can accept the AI recommendation or override it. Your decisions and feedback comments will be permanently captured into long-term memory to inform future processing.
                </p>
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">
                  Reviewer Notes / Justification:
                </label>
                <textarea
                  rows={3}
                  value={reviewComment}
                  onChange={(e) => setReviewComment(e.target.value)}
                  placeholder="E.g., Approved after vendor confirmation of additional license quantity..."
                  className="w-full p-2.5 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500/20 text-slate-800"
                />
              </div>

              <div className="flex items-center gap-3 pt-2">
                <button
                  onClick={() => handleReviewAction('APPROVE')}
                  disabled={reviewSubmitting}
                  className="flex-1 py-2.5 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-sm transition-colors flex items-center justify-center gap-2"
                >
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Authorize & Approve</span>
                </button>

                <button
                  onClick={() => handleReviewAction('REJECT')}
                  disabled={reviewSubmitting}
                  className="flex-1 py-2.5 px-4 rounded-xl bg-rose-600 hover:bg-rose-700 text-white font-bold text-xs shadow-sm transition-colors flex items-center justify-center gap-2"
                >
                  <XCircle className="w-4 h-4" />
                  <span>Reject Transaction</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
