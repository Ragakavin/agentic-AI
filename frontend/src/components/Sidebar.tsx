import React from 'react';
import {
  LayoutDashboard, FileSpreadsheet, Upload, CheckSquare,
  Building2, ShoppingCart, Bot, Activity, BarChart3, FileDown,
  Bell, History, Settings, Sparkles, Layers
} from 'lucide-react';

interface SidebarProps {
  currentPage: string;
  onNavigate: (page: string) => void;
  pendingReviewCount?: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentPage,
  onNavigate,
  pendingReviewCount = 0
}) => {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'invoices', label: 'Invoices', icon: FileSpreadsheet },
    { id: 'upload', label: 'Upload Invoice', icon: Upload },
    { id: 'review', label: 'Review Queue', icon: CheckSquare, badge: pendingReviewCount },
    { id: 'vendors', label: 'Vendors', icon: Building2 },
    { id: 'purchase-orders', label: 'Purchase Orders', icon: ShoppingCart },
    { id: 'ai-assistant', label: 'AI Assistant', icon: Bot, isNew: true },
    { id: 'agents', label: 'Agent Monitor', icon: Activity },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'reports', label: 'Reports', icon: FileDown },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'audit-logs', label: 'Audit Logs', icon: History },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col shrink-0 h-screen sticky top-0 border-r border-slate-800 select-none">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800 flex items-center gap-3">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-brand-600 to-blue-500 flex items-center justify-center text-white shadow-md">
          <Layers className="w-5 h-5" />
        </div>
        <div>
          <div className="text-sm font-extrabold text-white tracking-tight flex items-center gap-1.5">
            Agentic Invoice
            <span className="text-[10px] bg-emerald-500/20 text-emerald-400 font-semibold px-1.5 py-0.5 rounded border border-emerald-500/30">
              AI
            </span>
          </div>
          <div className="text-[11px] text-slate-400 font-medium">Enterprise Orchestrator</div>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        <div className="px-3 py-1 text-[10px] font-bold uppercase tracking-wider text-slate-500">
          Core Operations
        </div>

        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentPage === item.id;

          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                isActive
                  ? 'bg-slate-800 text-white font-semibold border-l-3 border-brand-500 shadow-xs'
                  : 'hover:bg-slate-800/60 text-slate-400 hover:text-slate-200'
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon className={`w-4 h-4 ${isActive ? 'text-brand-400' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </div>

              {item.badge !== undefined && item.badge > 0 && (
                <span className="px-1.5 py-0.5 text-[10px] font-bold rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30">
                  {item.badge}
                </span>
              )}

              {item.isNew && (
                <span className="flex items-center gap-0.5 px-1.5 py-0.5 text-[9px] font-bold rounded-md bg-purple-500/20 text-purple-300">
                  <Sparkles className="w-2.5 h-2.5" />
                  RAG
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Status Footer */}
      <div className="p-4 border-t border-slate-800 bg-slate-950/40 text-xs">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="text-[11px]">System Status</span>
          <span className="inline-flex items-center gap-1.5 text-emerald-400 text-[11px] font-semibold">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            10 Agents Active
          </span>
        </div>
        <div className="text-[10px] text-slate-500">
          FastAPI + Ollama / Local Fallback
        </div>
      </div>
    </aside>
  );
};
