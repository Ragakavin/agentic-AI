import React, { useState, useEffect } from 'react';
import {
  Bell, Search, Upload, Play, RefreshCw, UserCheck, Check,
  AlertTriangle, Shield, CheckCircle2, ChevronDown, ExternalLink
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import { NotificationItem } from '../types';

interface HeaderProps {
  onNavigate: (page: string, param?: any) => void;
  onRefresh?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onNavigate, onRefresh }) => {
  const { user, switchRole } = useAuth();
  const [unreadCount, setUnreadCount] = useState<number>(0);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [showNotifs, setShowNotifs] = useState(false);
  const [showRoles, setShowRoles] = useState(false);
  const [showDemoCases, setShowDemoCases] = useState(false);
  const [triggeringDemo, setTriggeringDemo] = useState(false);

  useEffect(() => {
    loadNotifications();
    const interval = setInterval(loadNotifications, 10000);
    return () => clearInterval(interval);
  }, []);

  const loadNotifications = async () => {
    try {
      const { unread_count } = await api.getUnreadNotificationCount();
      setUnreadCount(unread_count);
      const items = await api.getNotifications();
      setNotifications(items.slice(0, 6));
    } catch {
      // ignore
    }
  };

  const handleRunDemo = async (caseKey: string) => {
    setTriggeringDemo(true);
    setShowDemoCases(false);
    try {
      const res = await api.triggerDemoCase(caseKey);
      if (onRefresh) onRefresh();
      onNavigate('invoice-details', res.analysis.invoice_id);
    } catch (err: any) {
      alert(`Demo trigger failed: ${err.message}`);
    } finally {
      setTriggeringDemo(false);
    }
  };

  const handleResetDb = async () => {
    if (confirm('Reset system database to benchmark initial state?')) {
      try {
        await api.resetDemoDatabase();
        if (onRefresh) onRefresh();
        alert('Database reseeded successfully with benchmark demo records.');
      } catch (err: any) {
        alert(err.message);
      }
    }
  };

  return (
    <header className="sticky top-0 z-30 bg-white/95 backdrop-blur-md border-b border-slate-200 px-6 py-3 flex items-center justify-between shadow-2xs">
      {/* Search Input */}
      <div className="flex items-center gap-3 w-72 md:w-96">
        <div className="relative w-full">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search invoices, vendors, POs, Tax IDs..."
            className="w-full pl-9 pr-4 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 text-slate-800 transition-all"
            onKeyDown={(e) => {
              if (e.key === 'Enter' && e.currentTarget.value) {
                onNavigate('invoices', e.currentTarget.value);
              }
            }}
          />
        </div>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-2.5">
        {/* Demo Presets Menu */}
        <div className="relative">
          <button
            onClick={() => setShowDemoCases(!showDemoCases)}
            disabled={triggeringDemo}
            className="inline-flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-semibold text-emerald-800 bg-emerald-50 hover:bg-emerald-100/80 border border-emerald-200 rounded-lg transition-colors"
          >
            <Play className={`w-3.5 h-3.5 text-emerald-600 ${triggeringDemo ? 'animate-spin' : ''}`} />
            <span>Run Benchmark Demo</span>
            <ChevronDown className="w-3 h-3 opacity-60" />
          </button>

          {showDemoCases && (
            <div className="absolute right-0 mt-2 w-72 bg-white rounded-xl shadow-xl border border-slate-200 p-2 z-50 animate-fadeIn">
              <div className="px-3 py-1.5 border-b border-slate-100 mb-1">
                <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
                  Automated Scenarios
                </span>
              </div>
              <button
                onClick={() => handleRunDemo('clean')}
                className="w-full text-left p-2.5 rounded-lg hover:bg-emerald-50 transition-colors flex items-start gap-2.5"
              >
                <CheckCircle2 className="w-4 h-4 text-emerald-600 mt-0.5" />
                <div>
                  <div className="text-xs font-bold text-slate-800">1. Clean Invoice (₹59,000)</div>
                  <div className="text-[11px] text-slate-500">ABC Technologies • 18% GST • Auto-Approve</div>
                </div>
              </button>

              <button
                onClick={() => handleRunDemo('po_mismatch')}
                className="w-full text-left p-2.5 rounded-lg hover:bg-amber-50 transition-colors flex items-start gap-2.5"
              >
                <AlertTriangle className="w-4 h-4 text-amber-600 mt-0.5" />
                <div>
                  <div className="text-xs font-bold text-slate-800">2. PO Mismatch (₹125,000)</div>
                  <div className="text-[11px] text-slate-500">XYZ Solutions • Qty 120 vs PO 100 • Review</div>
                </div>
              </button>

              <button
                onClick={() => handleRunDemo('duplicate')}
                className="w-full text-left p-2.5 rounded-lg hover:bg-rose-50 transition-colors flex items-start gap-2.5"
              >
                <AlertTriangle className="w-4 h-4 text-rose-600 mt-0.5" />
                <div>
                  <div className="text-xs font-bold text-slate-800">3. Duplicate Invoice (94% Sim)</div>
                  <div className="text-[11px] text-slate-500">ABC Technology • Duplicate INV-10025</div>
                </div>
              </button>

              <button
                onClick={() => handleRunDemo('tax_mismatch')}
                className="w-full text-left p-2.5 rounded-lg hover:bg-amber-50 transition-colors flex items-start gap-2.5"
              >
                <AlertTriangle className="w-4 h-4 text-amber-600 mt-0.5" />
                <div>
                  <div className="text-xs font-bold text-slate-800">4. Tax Mismatch (28% vs 18%)</div>
                  <div className="text-[11px] text-slate-500">Delta Systems • Rate Discrepancy</div>
                </div>
              </button>

              <div className="border-t border-slate-100 mt-2 pt-1.5 flex justify-between px-2">
                <button
                  onClick={handleResetDb}
                  className="text-[11px] font-semibold text-slate-500 hover:text-rose-600 flex items-center gap-1"
                >
                  <RefreshCw className="w-3 h-3" /> Reset Database
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Upload Invoice Button */}
        <button
          onClick={() => onNavigate('upload')}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-white bg-slate-900 hover:bg-slate-800 rounded-lg shadow-2xs transition-colors"
        >
          <Upload className="w-3.5 h-3.5" />
          <span>Upload</span>
        </button>

        {/* Notification Center Bell */}
        <div className="relative">
          <button
            onClick={() => setShowNotifs(!showNotifs)}
            className="p-2 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg relative transition-colors"
          >
            <Bell className="w-4 h-4" />
            {unreadCount > 0 && (
              <span className="absolute top-1 right-1 w-4 h-4 bg-rose-500 text-white rounded-full text-[9px] font-bold flex items-center justify-center">
                {unreadCount}
              </span>
            )}
          </button>

          {showNotifs && (
            <div className="absolute right-0 mt-2 w-80 bg-white rounded-xl shadow-xl border border-slate-200 p-3 z-50">
              <div className="flex items-center justify-between border-b border-slate-100 pb-2 mb-2">
                <span className="text-xs font-bold text-slate-900">Notifications</span>
                <button
                  onClick={async () => {
                    await api.markAllNotificationsRead();
                    setUnreadCount(0);
                  }}
                  className="text-[10px] text-brand-600 hover:underline"
                >
                  Mark all read
                </button>
              </div>
              <div className="space-y-2 max-h-72 overflow-y-auto">
                {notifications.length === 0 ? (
                  <p className="text-xs text-slate-400 py-4 text-center">No alerts recorded.</p>
                ) : (
                  notifications.map(n => (
                    <div
                      key={n.id}
                      onClick={() => {
                        api.markNotificationRead(n.id);
                        if (n.invoice_id) onNavigate('invoice-details', n.invoice_id);
                        setShowNotifs(false);
                      }}
                      className={`p-2 rounded-lg text-xs cursor-pointer transition-colors ${
                        n.is_read ? 'bg-slate-50' : 'bg-blue-50/50 border border-blue-100'
                      } hover:bg-slate-100`}
                    >
                      <div className="font-semibold text-slate-800">{n.title}</div>
                      <div className="text-slate-500 text-[11px] line-clamp-2 mt-0.5">{n.message}</div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* Role Switcher Pill */}
        <div className="relative">
          <button
            onClick={() => setShowRoles(!showRoles)}
            className="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium rounded-lg border border-slate-200 bg-slate-50 hover:bg-slate-100 transition-colors text-slate-700"
          >
            <Shield className="w-3.5 h-3.5 text-blue-600" />
            <span className="capitalize">{user?.role.replace('_', ' ') || 'Admin'}</span>
            <ChevronDown className="w-3 h-3 text-slate-400" />
          </button>

          {showRoles && (
            <div className="absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-xl border border-slate-200 p-2 z-50">
              <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 px-2 py-1 mb-1">
                Switch Role Mode
              </div>
              {[
                { key: 'admin', title: 'Admin' },
                { key: 'finance_manager', title: 'Finance Manager' },
                { key: 'reviewer', title: 'Reviewer' },
                { key: 'viewer', title: 'Viewer (Read-Only)' }
              ].map(r => (
                <button
                  key={r.key}
                  onClick={() => {
                    switchRole(r.key);
                    setShowRoles(false);
                  }}
                  className={`w-full text-left px-2.5 py-1.5 rounded-lg text-xs flex items-center justify-between ${
                    user?.role === r.key ? 'bg-brand-50 text-brand-700 font-semibold' : 'text-slate-700 hover:bg-slate-100'
                  }`}
                >
                  <span>{r.title}</span>
                  {user?.role === r.key && <Check className="w-3.5 h-3.5 text-brand-600" />}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
