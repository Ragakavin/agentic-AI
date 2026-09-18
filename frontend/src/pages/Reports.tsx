import React, { useState, useEffect } from 'react';
import { Download, FileSpreadsheet, FileText, RefreshCw } from 'lucide-react';
import { api } from '../services/api';
import { InvoiceSummary } from '../types';

export const Reports: React.FC = () => {
  const [invoices, setInvoices] = useState<InvoiceSummary[]>([]);
  const [reportsList, setReportsList] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [generatingId, setGeneratingId] = useState<number | null>(null);
  const [selectedFormat, setSelectedFormat] = useState<'PDF' | 'EXCEL' | 'CSV'>('PDF');

  const loadData = async () => {
    setLoading(true);
    try {
      const [invs, reps] = await Promise.all([
        api.getInvoices(),
        api.listReports()
      ]);
      setInvoices(invs);
      setReportsList(reps);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleGenerate = async (invoiceId: number) => {
    setGeneratingId(invoiceId);
    try {
      const res = await api.generateReport(invoiceId, selectedFormat);
      await loadData();
      window.open(res.download_url, '_blank');
    } catch (err: any) {
      alert(err.message);
    } finally {
      setGeneratingId(null);
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn pb-16">
      <div>
        <h1 className="text-xl font-bold text-slate-900 tracking-tight">Compliance & Audit Report Center</h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Export exhaustive multi-agent verification dossiers in PDF, Excel, or CSV format
        </p>
      </div>

      {/* Format Selector Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold text-slate-700">Export Format:</span>
          {(['PDF', 'EXCEL', 'CSV'] as const).map(fmt => (
            <button
              key={fmt}
              onClick={() => setSelectedFormat(fmt)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                selectedFormat === fmt
                  ? 'bg-slate-900 text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {fmt}
            </button>
          ))}
        </div>
      </div>

      {/* Invoices List to Export */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-2xs overflow-hidden">
        <div className="p-4 border-b border-slate-100 bg-slate-50/70 text-xs font-bold text-slate-800 uppercase tracking-wider">
          Generate New Report for Invoice
        </div>

        {loading ? (
          <div className="py-16 text-center text-slate-400 text-xs">
            <RefreshCw className="w-6 h-6 animate-spin text-emerald-600 mx-auto mb-2" />
            <span>Loading invoices...</span>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-100/70 text-slate-600 text-[10px] font-semibold uppercase">
                <tr>
                  <th className="p-3">Invoice Number</th>
                  <th className="p-3">Vendor</th>
                  <th className="p-3">Amount</th>
                  <th className="p-3">Decision</th>
                  <th className="p-3">Risk Score</th>
                  <th className="p-3 text-right">Generate</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {invoices.map((inv) => (
                  <tr key={inv.id} className="hover:bg-slate-50">
                    <td className="p-3 font-bold text-slate-900 font-mono">
                      {inv.invoice_number || inv.invoice_id}
                    </td>
                    <td className="p-3 text-slate-700">{inv.vendor_name || 'N/A'}</td>
                    <td className="p-3 font-semibold font-mono">₹{inv.total_amount.toLocaleString()}</td>
                    <td className="p-3">
                      <span className="text-[11px] font-bold text-slate-700 uppercase">
                        {inv.final_decision || inv.status}
                      </span>
                    </td>
                    <td className="p-3 font-mono text-slate-600">{inv.risk_score.toFixed(0)}/100</td>
                    <td className="p-3 text-right">
                      <button
                        onClick={() => handleGenerate(inv.id)}
                        disabled={generatingId === inv.id}
                        className="px-3 py-1 rounded-lg bg-brand-50 hover:bg-brand-100 text-brand-700 border border-brand-200 text-xs font-semibold inline-flex items-center gap-1.5 transition-colors"
                      >
                        <Download className={`w-3.5 h-3.5 ${generatingId === inv.id ? 'animate-spin' : ''}`} />
                        <span>Download {selectedFormat}</span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Recent Generated Reports Table */}
      {reportsList.length > 0 && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-2xs overflow-hidden">
          <div className="p-4 border-b border-slate-100 bg-slate-50/70 text-xs font-bold text-slate-800 uppercase tracking-wider">
            Recently Exported Archives
          </div>
          <div className="divide-y divide-slate-100 text-xs">
            {reportsList.map((rep) => (
              <div key={rep.id} className="p-3.5 flex items-center justify-between hover:bg-slate-50">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-blue-50 text-blue-600">
                    {rep.report_type === 'PDF' ? <FileText className="w-4 h-4" /> : <FileSpreadsheet className="w-4 h-4" />}
                  </div>
                  <div>
                    <span className="font-bold text-slate-900">{rep.filename}</span>
                    <div className="text-[11px] text-slate-500">
                      Invoice Ref: {rep.invoice_ref} • Format: {rep.report_type} • Size: {(rep.file_size_bytes / 1024).toFixed(1)} KB
                    </div>
                  </div>
                </div>

                <a
                  href={rep.download_url}
                  target="_blank"
                  rel="noreferrer"
                  className="px-3 py-1.5 rounded-lg border border-slate-200 bg-slate-50 hover:bg-slate-100 text-xs font-medium text-slate-700 inline-flex items-center gap-1"
                >
                  <Download className="w-3 h-3" />
                  <span>Download</span>
                </a>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
