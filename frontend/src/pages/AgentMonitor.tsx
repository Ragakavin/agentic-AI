import React, { useState, useEffect } from 'react';
import {
  Activity, CheckCircle2, AlertTriangle, Clock, Wrench, RefreshCw,
  Terminal, ShieldCheck, ChevronDown, ChevronRight
} from 'lucide-react';
import { api } from '../services/api';
import { AgentOverview, AgentRun } from '../types';

export const AgentMonitor: React.FC = () => {
  const [agents, setAgents] = useState<AgentOverview[]>([]);
  const [recentRuns, setRecentRuns] = useState<AgentRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedRun, setSelectedRun] = useState<AgentRun | null>(null);

  useEffect(() => {
    loadAgentData();
    const interval = setInterval(loadAgentData, 8000);
    return () => clearInterval(interval);
  }, []);

  const loadAgentData = async () => {
    try {
      const [overview, runs] = await Promise.all([
        api.getAgentsOverview(),
        api.getAgentRuns(25)
      ]);
      setAgents(overview);
      setRecentRuns(runs);
      if (runs.length > 0 && !selectedRun) setSelectedRun(runs[0]);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn pb-16">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">Agent Monitoring & Traceability</h1>
            <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
              Multi-Agent Orchestrator
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Real-time latency metrics, dynamic tool call telemetry, and deterministic state transitions across all 10 specialized agents
          </p>
        </div>

        <button
          onClick={loadAgentData}
          className="p-2 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-600 self-start"
          title="Refresh agent states"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* 10 Agent Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3">
        {agents.map((ag, i) => (
          <div
            key={i}
            className="p-4 rounded-xl border border-slate-200 bg-white shadow-2xs flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] font-mono text-slate-400 font-bold">AGENT #{i + 1}</span>
                <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded-full ${
                  ag.status === 'ACTIVE' ? 'bg-emerald-50 text-emerald-700' : (ag.status === 'WARNING' ? 'bg-amber-50 text-amber-700' : 'bg-slate-100 text-slate-600')
                }`}>
                  {ag.status}
                </span>
              </div>
              <h3 className="text-xs font-bold text-slate-900 leading-snug mb-1">{ag.name}</h3>
              <p className="text-[11px] text-slate-500 line-clamp-2 mb-3">{ag.role}</p>
            </div>

            <div className="space-y-1 text-[11px] border-t border-slate-100 pt-2.5 text-slate-600">
              <div className="flex justify-between">
                <span className="text-slate-400">Total Runs:</span>
                <span className="font-bold text-slate-800">{ag.total_runs}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Avg Latency:</span>
                <span className="font-mono text-slate-800">{ag.avg_latency_ms} ms</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Tool Calls:</span>
                <span className="font-semibold text-blue-700 font-mono">{ag.total_tool_calls}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Live Agent Execution Trace Log */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Runs List */}
        <div className="lg:col-span-6 bg-white rounded-2xl border border-slate-200 shadow-2xs overflow-hidden">
          <div className="p-3.5 border-b border-slate-100 bg-slate-50/70 text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center justify-between">
            <span>Recent Agent Runs & Invocations</span>
            <span className="text-slate-400 font-normal">Last 25 runs</span>
          </div>

          <div className="divide-y divide-slate-100 max-h-[500px] overflow-y-auto">
            {recentRuns.map((run) => (
              <div
                key={run.id}
                onClick={() => setSelectedRun(run)}
                className={`p-3.5 cursor-pointer transition-colors text-xs ${
                  selectedRun?.id === run.id ? 'bg-blue-50/60 border-l-4 border-blue-600' : 'hover:bg-slate-50'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="font-bold text-slate-900">{run.agent_name}</span>
                  <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                    run.status === 'COMPLETED' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
                  }`}>
                    {run.status}
                  </span>
                </div>
                <div className="flex items-center justify-between text-[11px] text-slate-500">
                  <span className="flex items-center gap-1 text-slate-400">
                    <Clock className="w-3 h-3" /> {run.execution_time_ms} ms
                  </span>
                  <span className="text-blue-700 font-semibold font-mono">
                    {run.tool_calls.length} dynamic tool call(s)
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Run Detail & Tool Calls JSON Inspector */}
        {selectedRun && (
          <div className="lg:col-span-6 bg-white rounded-2xl border border-slate-200 shadow-sm p-5 space-y-4">
            <div className="border-b border-slate-100 pb-3">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
                  <Terminal className="w-3.5 h-3.5 text-blue-600" />
                  Agent Execution Telemetry
                </h3>
                <span className="text-[10px] font-mono text-slate-400">ID #{selectedRun.id}</span>
              </div>
              <div className="text-xs text-slate-600 font-bold mt-1">{selectedRun.agent_name}</div>
              <div className="text-[11px] text-slate-400">
                Timestamp: {new Date(selectedRun.started_at).toLocaleTimeString()} • Execution: {selectedRun.execution_time_ms}ms
              </div>
            </div>

            {/* Tool Calls */}
            <div>
              <span className="text-xs font-bold text-slate-700 block mb-1.5">
                Dynamic Tool Invocations ({selectedRun.tool_calls.length})
              </span>
              {selectedRun.tool_calls.length === 0 ? (
                <p className="text-xs text-slate-400 italic">No external tool calls in this step.</p>
              ) : (
                <div className="space-y-2">
                  {selectedRun.tool_calls.map(tc => (
                    <div key={tc.id} className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs font-mono">
                      <div className="flex items-center justify-between text-blue-700 font-bold mb-1">
                        <span>{tc.tool_name}()</span>
                        <span className="text-[10px] text-slate-400">{tc.execution_time_ms}ms</span>
                      </div>
                      <div className="text-[10px] text-slate-500 mb-1">Result:</div>
                      <pre className="text-[10px] bg-white p-2 rounded border border-slate-200 overflow-x-auto text-slate-800">
                        {JSON.stringify(tc.tool_result, null, 2)}
                      </pre>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Output State */}
            <div>
              <span className="text-xs font-bold text-slate-700 block mb-1.5">
                Produced Output State Payload
              </span>
              <pre className="text-[10px] bg-slate-50 p-3 rounded-xl border border-slate-200 overflow-x-auto text-slate-800 max-h-48 overflow-y-auto font-mono">
                {JSON.stringify(selectedRun.output_data, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
