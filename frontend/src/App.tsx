import React, { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { Dashboard } from './pages/Dashboard';
import { Invoices } from './pages/Invoices';
import { InvoiceDetails } from './pages/InvoiceDetails';
import { UploadInvoice } from './pages/UploadInvoice';
import { ReviewQueue } from './pages/ReviewQueue';
import { Vendors } from './pages/Vendors';
import { PurchaseOrders } from './pages/PurchaseOrders';
import { AgentMonitor } from './pages/AgentMonitor';
import { Analytics } from './pages/Analytics';
import { Reports } from './pages/Reports';
import { Notifications } from './pages/Notifications';
import { AuditLogs } from './pages/AuditLogs';
import { AiAssistant } from './pages/AiAssistant';
import { Settings } from './pages/Settings';
import { Login } from './pages/Login';
import { api } from './services/api';

const AppContent: React.FC = () => {
  const { user } = useAuth();
  const [currentPage, setCurrentPage] = useState<string>('dashboard');
  const [selectedInvoiceId, setSelectedInvoiceId] = useState<number | null>(null);
  const [searchParam, setSearchParam] = useState<string>('');
  const [pendingCount, setPendingCount] = useState<number>(0);
  const [refreshTrigger, setRefreshTrigger] = useState<number>(0);

  useEffect(() => {
    const fetchPendingCount = async () => {
      try {
        const invs = await api.getInvoices({ status: 'review_required' });
        setPendingCount(invs.length);
      } catch {
        // ignore
      }
    };
    fetchPendingCount();
    const interval = setInterval(fetchPendingCount, 15000);
    return () => clearInterval(interval);
  }, [refreshTrigger]);

  const handleNavigate = (page: string, param?: any) => {
    if (page === 'invoice-details') {
      if (typeof param === 'number') {
        setSelectedInvoiceId(param);
      } else if (typeof param === 'string' && param.startsWith('INV-SYS-')) {
        // Find internal ID
        api.getInvoices({ search: param }).then(res => {
          if (res.length > 0) setSelectedInvoiceId(res[0].id);
        });
      }
      setCurrentPage('invoice-details');
    } else if (page === 'invoices' && typeof param === 'string') {
      setSearchParam(param);
      setCurrentPage('invoices');
    } else {
      setCurrentPage(page);
    }
  };

  const handleRefresh = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  if (!user) {
    return <Login onSuccess={() => setCurrentPage('dashboard')} />;
  }

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden font-sans text-slate-900">
      {/* Sidebar */}
      <Sidebar
        currentPage={currentPage}
        onNavigate={handleNavigate}
        pendingReviewCount={pendingCount}
      />

      {/* Main App Container */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Header */}
        <Header onNavigate={handleNavigate} onRefresh={handleRefresh} />

        {/* Scrollable Main Workspace */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8">
          {currentPage === 'dashboard' && <Dashboard onNavigate={handleNavigate} />}
          {currentPage === 'invoices' && <Invoices onNavigate={handleNavigate} initialSearch={searchParam} />}
          {currentPage === 'invoice-details' && selectedInvoiceId && (
            <InvoiceDetails invoiceId={selectedInvoiceId} onNavigate={handleNavigate} />
          )}
          {currentPage === 'upload' && <UploadInvoice onNavigate={handleNavigate} />}
          {currentPage === 'review' && <ReviewQueue onNavigate={handleNavigate} />}
          {currentPage === 'vendors' && <Vendors onNavigate={handleNavigate} />}
          {currentPage === 'purchase-orders' && <PurchaseOrders onNavigate={handleNavigate} />}
          {currentPage === 'agents' && <AgentMonitor />}
          {currentPage === 'analytics' && <Analytics />}
          {currentPage === 'reports' && <Reports />}
          {currentPage === 'notifications' && <Notifications onNavigate={handleNavigate} />}
          {currentPage === 'audit-logs' && <AuditLogs />}
          {currentPage === 'ai-assistant' && <AiAssistant />}
          {currentPage === 'settings' && <Settings />}
        </main>
      </div>
    </div>
  );
};

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}
