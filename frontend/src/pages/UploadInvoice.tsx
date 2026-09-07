import React, { useState, useRef } from 'react';
import {
  Upload, FileText, CheckCircle2, AlertTriangle, Play,
  RefreshCw, ShieldCheck, Sparkles, ArrowRight
} from 'lucide-react';
import { api } from '../services/api';

interface UploadInvoiceProps {
  onNavigate: (page: string, param?: any) => void;
}

const STAGES = [
  'Receiving & Verifying SHA-256 Checksum...',
  'Extracting Layout & Structured Line Items...',
  'Checking Statutory GST / VAT Compliance...',
  'Executing Three-Way Purchase Order Matching...',
  'Running 12-Factor Fraud & Anomaly Engine...',
  'Synthesizing Evidence & Generating LLM Decision...'
];

export const UploadInvoice: React.FC<UploadInvoiceProps> = ({ onNavigate }) => {
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [currentStageIdx, setCurrentStageIdx] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  const processFile = async (file: File) => {
    setUploading(true);
    setCurrentStageIdx(0);

    // Animate stages for realistic user feedback
    const interval = setInterval(() => {
      setCurrentStageIdx((prev) => (prev < STAGES.length - 1 ? prev + 1 : prev));
    }, 400);

    try {
      const res = await api.uploadInvoice(file, true);
      clearInterval(interval);
      setTimeout(() => {
        onNavigate('invoice-details', res.analysis.invoice_id);
      }, 500);
    } catch (err: any) {
      clearInterval(interval);
      alert(`Upload error: ${err.message}`);
      setUploading(false);
    }
  };

  const handleDemoPreset = async (caseKey: string) => {
    setUploading(true);
    setCurrentStageIdx(0);
    const interval = setInterval(() => {
      setCurrentStageIdx((prev) => (prev < STAGES.length - 1 ? prev + 1 : prev));
    }, 350);

    try {
      const res = await api.triggerDemoCase(caseKey);
      clearInterval(interval);
      setTimeout(() => {
        onNavigate('invoice-details', res.analysis.invoice_id);
      }, 500);
    } catch (err: any) {
      clearInterval(interval);
      alert(`Demo preset error: ${err.message}`);
      setUploading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fadeIn pb-16">
      <div>
        <h1 className="text-xl font-bold text-slate-900 tracking-tight">
          Invoice Ingestion & Autonomous Analysis
        </h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Drop PDF or image files to initiate the 10-agent validation, fraud scoring, and decision pipeline
        </p>
      </div>

      {/* Upload Zone */}
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        className={`relative border-2 border-dashed rounded-2xl p-10 text-center transition-all bg-white shadow-2xs ${
          dragActive
            ? 'border-emerald-500 bg-emerald-50/50 scale-[1.01]'
            : 'border-slate-300 hover:border-slate-400'
        } ${uploading ? 'pointer-events-none opacity-90' : ''}`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.png,.jpg,.jpeg,.webp"
          onChange={handleChange}
          className="hidden"
        />

        {!uploading ? (
          <div className="flex flex-col items-center justify-center space-y-3">
            <div className="w-14 h-14 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center shadow-xs">
              <Upload className="w-7 h-7" />
            </div>

            <div>
              <p className="text-sm font-bold text-slate-800">
                Drag and drop your invoice document here
              </p>
              <p className="text-xs text-slate-500 mt-1">
                Supports PDF, PNG, JPG, JPEG (Max 25MB)
              </p>
            </div>

            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold shadow-sm transition-colors"
            >
              Browse Local Files
            </button>
          </div>
        ) : (
          <div className="py-6 space-y-4">
            <div className="w-12 h-12 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center mx-auto animate-bounce">
              <Sparkles className="w-6 h-6" />
            </div>

            <div>
              <h3 className="text-sm font-bold text-slate-900">
                Autonomous Agents Processing Invoice...
              </h3>
              <p className="text-xs text-emerald-700 font-semibold mt-1">
                {STAGES[currentStageIdx]}
              </p>
            </div>

            {/* Progress Stepper */}
            <div className="max-w-md mx-auto w-full bg-slate-200 h-2 rounded-full overflow-hidden">
              <div
                className="bg-emerald-500 h-full transition-all duration-300 rounded-full"
                style={{ width: `${((currentStageIdx + 1) / STAGES.length) * 100}%` }}
              />
            </div>
          </div>
        )}
      </div>

      {/* 1-Click Demo Preset Benchmark Invoices */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-2xs space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800 flex items-center gap-1.5">
              <Play className="w-3.5 h-3.5 text-emerald-600" />
              1-Click Benchmark Invoices (Instant Demonstration)
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Test core agent capabilities without uploading custom files
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {[
            {
              key: 'clean',
              title: '1. Clean Invoice (Auto-Approve)',
              vendor: 'ABC Technologies',
              amount: '₹59,000',
              badge: 'Low Risk',
              badgeColor: 'bg-emerald-50 text-emerald-700 border-emerald-200',
              desc: 'Passes line items, 18% GST match, PO match -> Auto-Approved'
            },
            {
              key: 'po_mismatch',
              title: '2. PO Mismatch (Review Required)',
              vendor: 'XYZ Solutions',
              amount: '₹125,000',
              badge: 'High Risk',
              badgeColor: 'bg-amber-50 text-amber-700 border-amber-200',
              desc: 'Invoice quantity (120) exceeds PO quantity (100) -> Flagged for review'
            },
            {
              key: 'duplicate',
              title: '3. Duplicate Transaction (Critical)',
              vendor: 'ABC Technology',
              amount: '₹59,000',
              badge: 'Critical',
              badgeColor: 'bg-rose-50 text-rose-700 border-rose-200',
              desc: 'Fuzzy similarity 94% with prior invoice INV-10025 -> Flagged'
            },
            {
              key: 'tax_mismatch',
              title: '4. Tax Schedule Mismatch',
              vendor: 'Delta Systems',
              amount: '₹102,400',
              badge: 'High Risk',
              badgeColor: 'bg-amber-50 text-amber-700 border-amber-200',
              desc: 'Invoice tax 28% differs from expected statutory rate 18% -> Flagged'
            }
          ].map(demo => (
            <div
              key={demo.key}
              onClick={() => handleDemoPreset(demo.key)}
              className="p-4 rounded-xl border border-slate-200 hover:border-emerald-300 hover:bg-emerald-50/20 cursor-pointer transition-all flex flex-col justify-between group"
            >
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-xs font-bold text-slate-800 group-hover:text-emerald-700">
                    {demo.title}
                  </span>
                  <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded border ${demo.badgeColor}`}>
                    {demo.badge}
                  </span>
                </div>
                <p className="text-[11px] text-slate-500 mb-2 leading-relaxed">
                  {demo.desc}
                </p>
              </div>

              <div className="flex items-center justify-between pt-2 border-t border-slate-100 text-xs text-slate-600 font-medium">
                <span>{demo.vendor} • {demo.amount}</span>
                <span className="text-emerald-600 font-bold flex items-center gap-1 group-hover:translate-x-0.5 transition-transform">
                  Run <ArrowRight className="w-3 h-3" />
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
