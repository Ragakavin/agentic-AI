import React from 'react';
import { CheckCircle2, AlertTriangle, XCircle, Clock, HelpCircle } from 'lucide-react';

interface StatusBadgeProps {
  status?: string;
  decision?: string;
  size?: 'sm' | 'md' | 'lg';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, decision, size = 'md' }) => {
  const target = (decision || status || '').toUpperCase();

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5 gap-1',
    md: 'text-xs px-2.5 py-1 gap-1.5 font-medium',
    lg: 'text-sm px-3 py-1.5 gap-2 font-medium'
  };

  if (target === 'APPROVE' || target === 'APPROVED') {
    return (
      <span className={`inline-flex items-center rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200/80 ${sizeClasses[size]}`}>
        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
        Approved
      </span>
    );
  }

  if (target === 'REVIEW' || target === 'REVIEW_REQUIRED' || target === 'PENDING') {
    return (
      <span className={`inline-flex items-center rounded-full bg-amber-50 text-amber-700 border border-amber-200/80 ${sizeClasses[size]}`}>
        <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
        Review Required
      </span>
    );
  }

  if (target === 'REJECT' || target === 'REJECTED') {
    return (
      <span className={`inline-flex items-center rounded-full bg-rose-50 text-rose-700 border border-rose-200/80 ${sizeClasses[size]}`}>
        <XCircle className="w-3.5 h-3.5 text-rose-600" />
        Rejected
      </span>
    );
  }

  if (target === 'PROCESSING') {
    return (
      <span className={`inline-flex items-center rounded-full bg-blue-50 text-blue-700 border border-blue-200/80 animate-pulse ${sizeClasses[size]}`}>
        <Clock className="w-3.5 h-3.5 text-blue-600" />
        Processing Agents...
      </span>
    );
  }

  return (
    <span className={`inline-flex items-center rounded-full bg-slate-100 text-slate-700 border border-slate-200 ${sizeClasses[size]}`}>
      <HelpCircle className="w-3.5 h-3.5 text-slate-500" />
      {target || 'Received'}
    </span>
  );
};
