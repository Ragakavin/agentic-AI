import React, { useState } from 'react';
import { Layers, ArrowRight, Lock, Mail } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

interface LoginProps {
  onSuccess: () => void;
}

export const Login: React.FC<LoginProps> = ({ onSuccess }) => {
  const { login, switchRole } = useAuth();
  const [email, setEmail] = useState('admin@enterprise.ai');
  const [password, setPassword] = useState('admin123');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await login(email, password);
      onSuccess();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickLogin = async (role: string) => {
    setLoading(true);
    try {
      await switchRole(role);
      onSuccess();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-3xl border border-slate-200 shadow-xl p-8 space-y-6">
        {/* Brand */}
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-brand-600 to-blue-600 flex items-center justify-center text-white mx-auto shadow-md">
            <Layers className="w-6 h-6" />
          </div>
          <h1 className="text-xl font-extrabold text-slate-900 tracking-tight">
            Intelligent Invoice Agent
          </h1>
          <p className="text-xs text-slate-500">
            Autonomous Accounts Payable Processing & Multi-Agent Verification
          </p>
        </div>

        {error && (
          <div className="p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-xl font-medium">
            {error}
          </div>
        )}

        {/* Credentials Form */}
        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          <div>
            <label className="font-semibold text-slate-700 block mb-1">Email Address</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full pl-9 pr-3 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500/20 text-slate-900"
              />
            </div>
          </div>

          <div>
            <label className="font-semibold text-slate-700 block mb-1">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full pl-9 pr-3 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500/20 text-slate-900"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs shadow-sm transition-colors flex items-center justify-center gap-2"
          >
            <span>{loading ? 'Authenticating...' : 'Sign In to Workspace'}</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </form>

        {/* Quick Demo Role Logins */}
        <div className="border-t border-slate-100 pt-5 space-y-2">
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block text-center">
            Or 1-Click Demo Login As:
          </span>

          <div className="grid grid-cols-2 gap-2 text-xs">
            <button
              onClick={() => handleQuickLogin('admin')}
              className="p-2.5 rounded-xl bg-slate-50 hover:bg-emerald-50/50 border border-slate-200 text-left transition-colors"
            >
              <div className="font-bold text-slate-800">Admin</div>
              <div className="text-[10px] text-slate-400">Full System Access</div>
            </button>

            <button
              onClick={() => handleQuickLogin('finance_manager')}
              className="p-2.5 rounded-xl bg-slate-50 hover:bg-blue-50/50 border border-slate-200 text-left transition-colors"
            >
              <div className="font-bold text-slate-800">Finance Manager</div>
              <div className="text-[10px] text-slate-400">Approvals & Reports</div>
            </button>

            <button
              onClick={() => handleQuickLogin('reviewer')}
              className="p-2.5 rounded-xl bg-slate-50 hover:bg-amber-50/50 border border-slate-200 text-left transition-colors"
            >
              <div className="font-bold text-slate-800">Reviewer</div>
              <div className="text-[10px] text-slate-400">HITL Review Queue</div>
            </button>

            <button
              onClick={() => handleQuickLogin('viewer')}
              className="p-2.5 rounded-xl bg-slate-50 hover:bg-purple-50/50 border border-slate-200 text-left transition-colors"
            >
              <div className="font-bold text-slate-800">Viewer</div>
              <div className="text-[10px] text-slate-400">Read-Only Analytics</div>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
