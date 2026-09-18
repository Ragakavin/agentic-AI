import React, { useState, useEffect, useCallback } from 'react';
import { RefreshCw } from 'lucide-react';
import { api } from '../services/api';
import { PurchaseOrder } from '../types';

interface PurchaseOrdersProps {
  onNavigate?: (page: string, param?: any) => void;
}

export const PurchaseOrders: React.FC<PurchaseOrdersProps> = ({ onNavigate: _onNavigate }) => {
  const [orders, setOrders] = useState<PurchaseOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPO, setSelectedPO] = useState<PurchaseOrder | null>(null);

  const loadOrders = useCallback(async () => {
    try {
      const data = await api.getPurchaseOrders();
      setOrders(data);
      if (data.length > 0 && !selectedPO) setSelectedPO(data[0]);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [selectedPO]);

  useEffect(() => {
    loadOrders();
  }, [loadOrders]);

  return (
    <div className="space-y-6 animate-fadeIn pb-16">
      <div>
        <h1 className="text-xl font-bold text-slate-900 tracking-tight">Purchase Order Master</h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Authorized ERP Purchase Orders against which incoming invoices are matched with configured tolerances
        </p>
      </div>

      {loading ? (
        <div className="py-20 text-center text-slate-400 text-xs">
          <RefreshCw className="w-6 h-6 animate-spin text-emerald-600 mx-auto mb-2" />
          <span>Loading purchase orders...</span>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Orders List */}
          <div className="lg:col-span-5 bg-white rounded-2xl border border-slate-200 shadow-2xs overflow-hidden">
            <div className="p-3.5 border-b border-slate-100 bg-slate-50/70 text-xs font-bold text-slate-700 uppercase tracking-wider">
              Purchase Orders ({orders.length})
            </div>
            <div className="divide-y divide-slate-100">
              {orders.map((po) => (
                <div
                  key={po.id}
                  onClick={() => setSelectedPO(po)}
                  className={`p-4 cursor-pointer transition-colors ${
                    selectedPO?.id === po.id ? 'bg-blue-50/50 border-l-4 border-blue-600' : 'hover:bg-slate-50'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-bold text-slate-900 font-mono">
                      {po.po_number}
                    </span>
                    <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200">
                      {po.status}
                    </span>
                  </div>
                  <div className="text-xs text-slate-600 font-medium">
                    {po.vendor_name || 'Vendor N/A'}
                  </div>
                  <div className="flex items-center justify-between mt-2 text-xs">
                    <span className="font-bold text-slate-900 font-mono">₹{po.total_amount.toLocaleString()}</span>
                    <span className="text-[11px] text-slate-400">{po.items.length} line item(s)</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* PO Details Panel */}
          {selectedPO && (
            <div className="lg:col-span-7 bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-5">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <div>
                  <h3 className="text-sm font-bold text-slate-900 font-mono">
                    {selectedPO.po_number} Details
                  </h3>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Authorized for {selectedPO.vendor_name}
                  </p>
                </div>
                <div className="text-right">
                  <span className="text-xs text-slate-400 block">Total Authorized</span>
                  <span className="text-base font-extrabold text-slate-900 font-mono">
                    ₹{selectedPO.total_amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                  </span>
                </div>
              </div>

              {/* Items Breakdown */}
              <div className="space-y-2">
                <span className="text-xs font-bold text-slate-700 uppercase tracking-wider block">
                  Authorized Line Items
                </span>
                <div className="border border-slate-200 rounded-xl overflow-hidden">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-slate-50 text-slate-600 font-semibold text-[10px] uppercase">
                      <tr>
                        <th className="p-2.5">Item Description</th>
                        <th className="p-2.5 text-right">Quantity</th>
                        <th className="p-2.5 text-right">Unit Price (₹)</th>
                        <th className="p-2.5 text-right">Total (₹)</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {selectedPO.items.map((item) => (
                        <tr key={item.id} className="hover:bg-slate-50">
                          <td className="p-2.5 font-medium text-slate-800">{item.item_description}</td>
                          <td className="p-2.5 text-right font-mono font-bold text-blue-700">{item.quantity}</td>
                          <td className="p-2.5 text-right font-mono">₹{item.unit_price.toLocaleString()}</td>
                          <td className="p-2.5 text-right font-bold font-mono">₹{item.total_price.toLocaleString()}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Tolerances info */}
              <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-600 flex items-center justify-between">
                <span>Matching Tolerances:</span>
                <span className="font-semibold text-slate-800 font-mono">±5.0% Quantity | ±3.0% Unit Price</span>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
