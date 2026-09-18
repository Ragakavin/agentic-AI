import React, { useState, useEffect, useCallback } from 'react';
import { Search, ArrowUpRight, RefreshCw } from 'lucide-react';
import { api } from '../services/api';
import { Vendor } from '../types';

interface VendorsProps {
  onNavigate: (page: string, param?: any) => void;
}

export const Vendors: React.FC<VendorsProps> = ({ onNavigate }) => {
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  const loadVendors = useCallback(async () => {
    try {
      const data = await api.getVendors();
      setVendors(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadVendors();
  }, [loadVendors]);

  const filtered = vendors.filter(v =>
    v.name.toLowerCase().includes(search.toLowerCase()) ||
    v.vendor_code.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 animate-fadeIn pb-16">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Vendor Management Master</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Verified vendor directory, Tax ID registry, historical spend deviations, and behavioral risk profiles
          </p>
        </div>
      </div>

      {/* Search Input */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs">
        <div className="relative max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search vendor name, code, or GSTIN..."
            className="w-full pl-9 pr-4 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500/20 text-slate-800"
          />
        </div>
      </div>

      {/* Vendor Cards Grid */}
      {loading ? (
        <div className="py-20 text-center text-slate-400 text-xs">
          <RefreshCw className="w-6 h-6 animate-spin text-emerald-600 mx-auto mb-2" />
          <span>Loading vendors...</span>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {filtered.map((v) => (
            <div
              key={v.id}
              className="bg-white rounded-2xl border border-slate-200 shadow-2xs p-5 flex flex-col justify-between hover:shadow-md transition-shadow"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-100 text-slate-600 font-bold">
                    {v.vendor_code}
                  </span>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                    v.risk_level === 'LOW'
                      ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                      : (v.risk_level === 'MEDIUM' ? 'bg-blue-50 text-blue-700 border border-blue-200' : 'bg-rose-50 text-rose-700 border border-rose-200')
                  }`}>
                    {v.risk_level} Risk
                  </span>
                </div>

                <h3 className="text-sm font-bold text-slate-900 tracking-tight mb-1">{v.name}</h3>
                <p className="text-[11px] text-slate-500 line-clamp-2 mb-3">{v.address || 'Address on record'}</p>

                <div className="space-y-1.5 text-xs border-t border-slate-100 pt-3 text-slate-600">
                  <div className="flex justify-between">
                    <span className="text-slate-400">GSTIN Tax ID:</span>
                    <span className="font-mono font-medium text-slate-800">{v.tax_id || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Total Invoices:</span>
                    <span className="font-semibold text-slate-800">{v.total_invoices_count}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Historical Avg:</span>
                    <span className="font-bold text-emerald-700 font-mono">₹{v.historical_avg_amount.toLocaleString()}</span>
                  </div>
                </div>
              </div>

              <div className="pt-4 border-t border-slate-100 mt-4 flex items-center justify-between text-xs">
                <span className="text-slate-400 text-[11px]">{v.bank_name || 'HDFC Bank'}</span>
                <button
                  onClick={() => onNavigate('invoices')}
                  className="text-brand-600 hover:text-brand-700 font-bold flex items-center gap-1 text-xs"
                >
                  View Invoices <ArrowUpRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
