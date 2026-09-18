import React, { useState, useEffect, useCallback } from 'react';
import { Search, RefreshCw, Terminal, User, Bot } from 'lucide-react';
import { api } from '../services/api';
import { AuditLogItem } from '../types';

export const AuditLogs: React.FC = () => {
  const [logs, setLogs] = useState<AuditLogItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [actorType, setActorType] = useState('ALL');
  const [selectedLog, setSelectedLog] = useState<AuditLogItem | null>(null);

  const loadLogs = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.getAuditLogs({
        actor_type: actorType !== 'ALL' ? actorType : undefined,
        search: search || undefined
      });
      setLogs(data);
      if (data.length > 0 && !selectedLog) setSelectedLog(data[0]);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [actorType, search, selectedLog]);

  useEffect(() => {
    loadLogs();
  }, [loadLogs]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadLogs();
  };

  return (
    <div className="space-y-6 animate-fadeIn pb-16">
      <div>
        <h1 className="text-xl font-bold text-slate-900 tracking-tight">Immutable Audit Trail</h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Tamper-evident record of all autonomous agent actions, financial validations, and human reviewer decisions
        </p>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs flex items-center justify-between gap-3">
        <form onSubmit={handleSearch} className="relative max-w-md w-full">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search action, actor, or entity ID..."
            className="w-full pl-9 pr-4 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500/20 text-slate-800"
          />
        </form>

        <div className="flex items-center gap-2 text-xs">
          <span className="text-slate-400 font-medium">Actor Type:</span>
          <select
            value={actorType}
            onChange={(e) => setActorType(e.target.value)}
            className="px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs font-medium text-slate-700 focus:outline-none"
          >
            <option value="ALL">All Actors</option>
            <option value="USER">Human Users</option>
            <option value="AGENT">Autonomous Agents</option>
          </select>
        </div>
      </div>

      {/* Main Split Layout: Logs list & Payload inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        <div className="lg:col-span-7 bg-white rounded-2xl border border-slate-200 shadow-2xs overflow-hidden">
          <div className="p-3.5 border-b border-slate-100 bg-slate-50/70 text-xs font-bold text-slate-700 uppercase tracking-wider">
            Audit Records ({logs.length})
          </div>

          {loading ? (
            <div className="py-20 text-center text-slate-400 text-xs">
              <RefreshCw className="w-6 h-6 animate-spin text-emerald-600 mx-auto mb-2" />
              <span>Loading audit trail...</span>
            </div>
          ) : logs.length === 0 ? (
            <div className="py-20 text-center text-slate-400 text-xs">
              No audit logs recorded matching search.
            </div>
          ) : (
            <div className="divide-y divide-slate-100 max-h-[550px] overflow-y-auto">
              {logs.map((log) => {
                const isAgent = log.actor_type === 'AGENT';
                const isSelected = selectedLog?.id === log.id;

                return (
                  <div
                    key={log.id}
                    onClick={() => setSelectedLog(log)}
                    className={`p-3.5 cursor-pointer transition-colors text-xs ${
                      isSelected ? 'bg-blue-50/50 border-l-4 border-blue-600' : 'hover:bg-slate-50'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-1.5 font-bold text-slate-900">
                        {isAgent ? (
                          <Bot className="w-3.5 h-3.5 text-brand-600" />
                        ) : (
                          <User className="w-3.5 h-3.5 text-blue-600" />
                        )}
                        <span>{log.actor_name}</span>
                      </div>
                      <span className="font-mono text-[10px] text-slate-400">
                        {new Date(log.timestamp).toLocaleTimeString()}
                      </span>
                    </div>

                    <div className="text-slate-700 font-mono text-[11px] font-semibold">
                      {log.action}
                    </div>

                    <div className="flex items-center justify-between text-[10px] text-slate-400 mt-1">
                      <span>Entity: {log.entity} #{log.entity_id || 'N/A'}</span>
                      <span className="text-emerald-700 font-bold">{log.result}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Payload Inspector */}
        {selectedLog && (
          <div className="lg:col-span-5 bg-white rounded-2xl border border-slate-200 shadow-sm p-5 space-y-4">
            <div className="border-b border-slate-100 pb-3">
              <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
                <Terminal className="w-3.5 h-3.5 text-blue-600" />
                Audit Entry State Diff Inspector
              </h3>
              <div className="text-xs font-bold text-slate-800 mt-1">
                {selectedLog.action}
              </div>
              <div className="text-[11px] text-slate-400 font-mono">
                Actor: {selectedLog.actor_name} ({selectedLog.actor_type})
              </div>
            </div>

            <div>
              <span className="text-xs font-semibold text-slate-700 block mb-1">Before State</span>
              <pre className="text-[10px] bg-slate-50 p-3 rounded-lg border border-slate-200 overflow-x-auto text-slate-700 font-mono max-h-36">
                {selectedLog.before_state ? JSON.stringify(selectedLog.before_state, null, 2) : 'null (initial state)'}
              </pre>
            </div>

            <div>
              <span className="text-xs font-semibold text-slate-700 block mb-1">After State</span>
              <pre className="text-[10px] bg-slate-50 p-3 rounded-lg border border-slate-200 overflow-x-auto text-slate-700 font-mono max-h-48">
                {selectedLog.after_state ? JSON.stringify(selectedLog.after_state, null, 2) : 'null'}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
