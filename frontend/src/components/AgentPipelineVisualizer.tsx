import React, { useState } from 'react';
import {
  FileText, Scan, Calculator, Percent, Copy, SplitSquareVertical,
  Building2, ShieldAlert, BrainCircuit, CheckSquare, ChevronDown, ChevronRight, Wrench
} from 'lucide-react';
import { AgentRun } from '../types';

interface AgentPipelineVisualizerProps {
  runs?: AgentRun[];
  isProcessing?: boolean;
}

const AGENT_STAGES = [
  { key: 'Invoice Intake Agent', title: 'Intake', icon: FileText, desc: 'Ingestion & SHA256' },
  { key: 'Document Extraction Agent', title: 'Extraction', icon: Scan, desc: 'Layout & Fields' },
  { key: 'Vendor Verification Agent', title: 'Vendor', icon: Building2, desc: 'Master & Deviation' },
  { key: 'Purchase Order Matching Agent', title: 'PO Match', icon: SplitSquareVertical, desc: 'Line Tolerance' },
  { key: 'Invoice Validation Agent', title: 'Validation', icon: Calculator, desc: 'Math Integrity' },
  { key: 'Tax Validation Agent', title: 'Tax Check', icon: Percent, desc: 'GST / VAT Rules' },
  { key: 'Duplicate Detection Agent', title: 'Duplicate', icon: Copy, desc: 'Fuzzy & Hash' },
  { key: 'Fraud and Anomaly Detection Agent', title: 'Fraud & Risk', icon: ShieldAlert, desc: '12 Indicators' },
  { key: 'AI Reasoning Agent', title: 'LLM Reason', icon: BrainCircuit, desc: 'Multi-Agent Synthesis' },
  { key: 'Decision Agent', title: 'Decision', icon: CheckSquare, desc: 'Confidence Routing' },
];

export const AgentPipelineVisualizer: React.FC<AgentPipelineVisualizerProps> = ({
  runs = [],
  isProcessing = false
}) => {
  const [expandedAgent, setExpandedAgent] = useState<string | null>(null);

  const getRunForStage = (stageName: string) => {
    return runs.find(r => r.agent_name === stageName);
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <BrainCircuit className="w-4 h-4 text-brand-600" />
            10-Agent Collaborative Autonomous Pipeline
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Real-time execution trace, tool invocations, and multi-agent reasoning flow
          </p>
        </div>
        {isProcessing && (
          <span className="inline-flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 rounded-full bg-blue-50 text-blue-700 animate-pulse">
            <span className="w-2 h-2 rounded-full bg-blue-600 animate-ping" />
            Orchestrating Agents...
          </span>
        )}
      </div>

      {/* Horizontal / Grid Pipeline Stream */}
      <div className="grid grid-cols-2 sm:grid-cols-5 lg:grid-cols-10 gap-2.5">
        {AGENT_STAGES.map((stage, idx) => {
          const run = getRunForStage(stage.key);
          const Icon = stage.icon;

          let statusBg = 'bg-slate-50 border-slate-200 text-slate-400';
          let badgeText = 'Pending';
          let badgeColor = 'bg-slate-100 text-slate-500';

          if (run) {
            if (run.status === 'COMPLETED') {
              statusBg = 'bg-emerald-50/70 border-emerald-300 text-emerald-700';
              badgeText = `${run.execution_time_ms}ms`;
              badgeColor = 'bg-emerald-100 text-emerald-800';
            } else if (run.status === 'WARNING') {
              statusBg = 'bg-amber-50/70 border-amber-300 text-amber-700';
              badgeText = 'Warning';
              badgeColor = 'bg-amber-100 text-amber-800';
            } else if (run.status === 'FAILED') {
              statusBg = 'bg-rose-50 border-rose-300 text-rose-700';
              badgeText = 'Failed';
              badgeColor = 'bg-rose-100 text-rose-800';
            }
          } else if (isProcessing && idx === runs.length) {
            statusBg = 'bg-blue-50 border-blue-400 text-blue-700 animate-pulse';
            badgeText = 'Running';
            badgeColor = 'bg-blue-100 text-blue-800';
          }

          const isExpanded = expandedAgent === stage.key;

          return (
            <div
              key={stage.key}
              onClick={() => run && setExpandedAgent(isExpanded ? null : stage.key)}
              className={`p-3 rounded-lg border text-center flex flex-col items-center justify-between transition-all cursor-pointer select-none hover:shadow-sm ${statusBg} ${
                isExpanded ? 'ring-2 ring-emerald-500' : ''
              }`}
            >
              <div className="flex items-center justify-between w-full text-[10px] font-mono text-slate-400 mb-1">
                <span>0{idx + 1}</span>
                {run?.tool_calls?.length ? (
                  <span className="flex items-center gap-0.5 text-blue-600 font-semibold" title={`${run.tool_calls.length} Tool Calls`}>
                    <Wrench className="w-2.5 h-2.5" />
                    {run.tool_calls.length}
                  </span>
                ) : null}
              </div>

              <div className="p-2 rounded-lg bg-white/80 shadow-xs mb-2">
                <Icon className="w-4 h-4" />
              </div>

              <span className="text-xs font-bold text-slate-800 truncate w-full mb-0.5">
                {stage.title}
              </span>
              <span className="text-[10px] text-slate-500 truncate w-full mb-2">
                {stage.desc}
              </span>

              <span className={`text-[10px] px-1.5 py-0.5 rounded font-medium ${badgeColor}`}>
                {badgeText}
              </span>
            </div>
          );
        })}
      </div>

      {/* Expanded Agent Tool Call & Data Inspector */}
      {expandedAgent && (
        <div className="mt-4 p-4 rounded-xl bg-slate-50 border border-slate-200 animate-fadeIn">
          {(() => {
            const selectedRun = getRunForStage(expandedAgent);
            if (!selectedRun) return null;

            return (
              <div>
                <div className="flex items-center justify-between border-b border-slate-200 pb-3 mb-3">
                  <div>
                    <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
                      <Wrench className="w-3.5 h-3.5 text-emerald-600" />
                      Agent Execution Inspector: {selectedRun.agent_name}
                    </h4>
                    <p className="text-[11px] text-slate-500 mt-0.5">
                      Completed in {selectedRun.execution_time_ms} ms | Status: {selectedRun.status}
                    </p>
                  </div>
                  <button
                    onClick={() => setExpandedAgent(null)}
                    className="text-xs text-slate-400 hover:text-slate-600"
                  >
                    Close
                  </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <span className="text-xs font-semibold text-slate-700 block mb-1">
                      Tool Calls Executed ({selectedRun.tool_calls.length})
                    </span>
                    {selectedRun.tool_calls.length === 0 ? (
                      <p className="text-xs text-slate-400 italic">No external tool calls required.</p>
                    ) : (
                      <div className="space-y-2">
                        {selectedRun.tool_calls.map(tc => (
                          <div key={tc.id} className="p-2.5 rounded-lg bg-white border border-slate-200 text-xs">
                            <div className="flex items-center justify-between font-mono font-semibold text-blue-700 mb-1">
                              <span>{tc.tool_name}()</span>
                              <span className="text-[10px] text-slate-400">{tc.execution_time_ms}ms</span>
                            </div>
                            <pre className="text-[10px] bg-slate-50 p-1.5 rounded overflow-x-auto text-slate-700">
                              {JSON.stringify(tc.tool_result, null, 2)}
                            </pre>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  <div>
                    <span className="text-xs font-semibold text-slate-700 block mb-1">
                      Agent Output State
                    </span>
                    <pre className="text-[10px] bg-white p-3 rounded-lg border border-slate-200 overflow-x-auto text-slate-700 max-h-48 overflow-y-auto">
                      {JSON.stringify(selectedRun.output_data, null, 2)}
                    </pre>
                  </div>
                </div>
              </div>
            );
          })()}
        </div>
      )}
    </div>
  );
};
