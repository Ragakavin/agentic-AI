import React from 'react';
import { ShieldAlert, ShieldCheck, AlertOctagon, AlertTriangle } from 'lucide-react';

interface RiskGaugeProps {
  score: number;
  level?: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  showDetail?: boolean;
}

export const RiskGauge: React.FC<RiskGaugeProps> = ({ score, level, showDetail = true }) => {
  const normalized = Math.min(100, Math.max(0, Math.round(score)));

  let derivedLevel = level;
  if (!derivedLevel) {
    if (normalized <= 30) derivedLevel = 'LOW';
    else if (normalized <= 60) derivedLevel = 'MEDIUM';
    else if (derivedLevel === undefined && normalized <= 80) derivedLevel = 'HIGH';
    else derivedLevel = 'CRITICAL';
  }

  const config = {
    LOW: {
      color: 'text-emerald-600',
      bg: 'bg-emerald-50',
      border: 'border-emerald-200',
      barBg: 'bg-emerald-500',
      icon: ShieldCheck,
      text: 'Low Risk'
    },
    MEDIUM: {
      color: 'text-blue-600',
      bg: 'bg-blue-50',
      border: 'border-blue-200',
      barBg: 'bg-blue-500',
      icon: AlertTriangle,
      text: 'Medium Risk'
    },
    HIGH: {
      color: 'text-amber-600',
      bg: 'bg-amber-50',
      border: 'border-amber-200',
      barBg: 'bg-amber-500',
      icon: ShieldAlert,
      text: 'High Risk'
    },
    CRITICAL: {
      color: 'text-rose-600',
      bg: 'bg-rose-50',
      border: 'border-rose-200',
      barBg: 'bg-rose-500',
      icon: AlertOctagon,
      text: 'Critical Risk'
    }
  }[derivedLevel] || {
    color: 'text-slate-600',
    bg: 'bg-slate-50',
    border: 'border-slate-200',
    barBg: 'bg-slate-500',
    icon: ShieldCheck,
    text: 'Unknown'
  };

  const Icon = config.icon;

  return (
    <div className={`p-4 rounded-xl border ${config.border} ${config.bg} flex flex-col gap-2.5`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Icon className={`w-5 h-5 ${config.color}`} />
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-700">
            Risk Assessment
          </span>
        </div>
        <span className={`text-xs font-bold px-2 py-0.5 rounded-md ${config.color} bg-white/80 border ${config.border}`}>
          {config.text}
        </span>
      </div>

      <div className="flex items-baseline gap-2">
        <span className={`text-3xl font-extrabold tracking-tight ${config.color}`}>
          {normalized}
        </span>
        <span className="text-sm font-medium text-slate-500">/ 100</span>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-slate-200/80 rounded-full h-2 overflow-hidden">
        <div
          className={`h-full ${config.barBg} transition-all duration-500 ease-out rounded-full`}
          style={{ width: `${normalized}%` }}
        />
      </div>

      {showDetail && (
        <p className="text-xs text-slate-600 mt-1 leading-relaxed">
          {normalized > 30
            ? 'Potential risk detected — human review recommended.'
            : 'All validation criteria within standard confidence bounds.'}
        </p>
      )}
    </div>
  );
};
