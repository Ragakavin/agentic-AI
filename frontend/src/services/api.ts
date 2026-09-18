import {
  InvoiceSummary, InvoiceDetail, AgentOverview, AgentRun, Vendor,
  PurchaseOrder, NotificationItem, AuditLogItem, AnalyticsData
} from '../types';

const API_BASE = '/api';

function getAuthHeader(): HeadersInit {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export const api = {
  // Authentication
  async login(email: string, password: string) {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Login failed');
    return res.json();
  },

  async switchRole(roleName: string) {
    const res = await fetch(`${API_BASE}/auth/switch-role/${roleName}`, {
      method: 'POST'
    });
    if (!res.ok) throw new Error('Failed to switch role');
    return res.json();
  },

  async getMe() {
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: getAuthHeader()
    });
    if (!res.ok) throw new Error('Not authenticated');
    return res.json();
  },

  // Invoices
  async getInvoices(params?: { status?: string; risk_level?: string; search?: string }): Promise<InvoiceSummary[]> {
    const query = new URLSearchParams();
    if (params?.status) query.append('status', params.status);
    if (params?.risk_level) query.append('risk_level', params.risk_level);
    if (params?.search) query.append('search', params.search);

    const res = await fetch(`${API_BASE}/invoices?${query.toString()}`, {
      headers: getAuthHeader()
    });
    if (!res.ok) throw new Error('Failed to fetch invoices');
    return res.json();
  },

  async getInvoiceDetail(id: number): Promise<InvoiceDetail> {
    const res = await fetch(`${API_BASE}/invoices/${id}`, {
      headers: getAuthHeader()
    });
    if (!res.ok) throw new Error('Failed to load invoice details');
    return res.json();
  },

  async uploadInvoice(file: File, autoAnalyze = true) {
    const formData = new FormData();
    formData.append('file', file);

    const res = await fetch(`${API_BASE}/invoices/upload?auto_analyze=${autoAnalyze}`, {
      method: 'POST',
      headers: getAuthHeader(),
      body: formData
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Upload failed');
    return res.json();
  },

  async reanalyzeInvoice(id: number) {
    const res = await fetch(`${API_BASE}/invoices/${id}/analyze`, {
      method: 'POST',
      headers: getAuthHeader()
    });
    if (!res.ok) throw new Error('Reanalysis failed');
    return res.json();
  },

  async reviewInvoice(id: number, decision: 'APPROVE' | 'REJECT', comments: string) {
    const res = await fetch(`${API_BASE}/invoices/${id}/review`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader()
      },
      body: JSON.stringify({ decision, comments })
    });
    if (!res.ok) throw new Error('Review action failed');
    return res.json();
  },

  // Vendors
  async getVendors(): Promise<Vendor[]> {
    const res = await fetch(`${API_BASE}/vendors`, {
      headers: getAuthHeader()
    });
    if (!res.ok) throw new Error('Failed to fetch vendors');
    return res.json();
  },

  async getVendorDetail(id: number): Promise<Vendor> {
    const res = await fetch(`${API_BASE}/vendors/${id}`, {
      headers: getAuthHeader()
    });
    if (!res.ok) throw new Error('Failed to fetch vendor');
    return res.json();
  },

  async getVendorInvoices(id: number) {
    const res = await fetch(`${API_BASE}/vendors/${id}/invoices`, {
      headers: getAuthHeader()
    });
    if (!res.ok) throw new Error('Failed to fetch vendor invoices');
    return res.json();
  },

  // Purchase Orders
  async getPurchaseOrders(): Promise<PurchaseOrder[]> {
    const res = await fetch(`${API_BASE}/purchase-orders`, {
      headers: getAuthHeader()
    });
    if (!res.ok) throw new Error('Failed to fetch purchase orders');
    return res.json();
  },

  // Agents
  async getAgentsOverview(): Promise<AgentOverview[]> {
    const res = await fetch(`${API_BASE}/agents/overview`, {
      headers: getAuthHeader()
    });
    if (!res.ok) throw new Error('Failed to fetch agents overview');
    return res.json();
  },

  async getAgentRuns(limit = 30): Promise<AgentRun[]> {
    const res = await fetch(`${API_BASE}/agents/runs?limit=${limit}`, {
      headers: getAuthHeader()
    });
    if (!res.ok) throw new Error('Failed to fetch agent runs');
    return res.json();
  },

  // Analytics
  async getAnalytics(): Promise<AnalyticsData> {
    const res = await fetch(`${API_BASE}/analytics/dashboard`, {
      headers: getAuthHeader()
    });
    if (!res.ok) throw new Error('Failed to fetch dashboard analytics');
    return res.json();
  },

  // Reports
  async generateReport(invoiceId: number, format: 'PDF' | 'EXCEL' | 'CSV') {
    const res = await fetch(`${API_BASE}/reports/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader()
      },
      body: JSON.stringify({ invoice_id: invoiceId, format })
    });
    if (!res.ok) throw new Error('Failed to generate report');
    return res.json();
  },

  async listReports() {
    const res = await fetch(`${API_BASE}/reports/list`, {
      headers: getAuthHeader()
    });
    if (!res.ok) throw new Error('Failed to fetch reports');
    return res.json();
  },

  // AI Assistant
  async askAi(content: string, invoiceId?: string) {
    const res = await fetch(`${API_BASE}/ai/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader()
      },
      body: JSON.stringify({ role: 'user', content, invoice_id: invoiceId })
    });
    if (!res.ok) throw new Error('Failed to consult AI assistant');
    return res.json();
  },

  // Notifications
  async getNotifications(): Promise<NotificationItem[]> {
    const res = await fetch(`${API_BASE}/notifications`, {
      headers: getAuthHeader()
    });
    if (!res.ok) throw new Error('Failed to fetch notifications');
    return res.json();
  },

  async getUnreadNotificationCount(): Promise<{ unread_count: number }> {
    const res = await fetch(`${API_BASE}/notifications/unread-count`, {
      headers: getAuthHeader()
    });
    if (!res.ok) return { unread_count: 0 };
    return res.json();
  },

  async markNotificationRead(id: number) {
    await fetch(`${API_BASE}/notifications/${id}/read`, {
      method: 'POST',
      headers: getAuthHeader()
    });
  },

  async markAllNotificationsRead() {
    await fetch(`${API_BASE}/notifications/read-all`, {
      method: 'POST',
      headers: getAuthHeader()
    });
  },

  // Audit Logs
  async getAuditLogs(params?: { actor_type?: string; action?: string; search?: string }): Promise<AuditLogItem[]> {
    const query = new URLSearchParams();
    if (params?.actor_type) query.append('actor_type', params.actor_type);
    if (params?.action) query.append('action', params.action);
    if (params?.search) query.append('search', params.search);

    const res = await fetch(`${API_BASE}/audit-logs?${query.toString()}`, {
      headers: getAuthHeader()
    });
    if (!res.ok) throw new Error('Failed to fetch audit logs');
    return res.json();
  },

  // Settings
  async getSettings() {
    const res = await fetch(`${API_BASE}/settings`, {
      headers: getAuthHeader()
    });
    if (!res.ok) throw new Error('Failed to fetch settings');
    return res.json();
  },

  async updateSettings(data: any) {
    const res = await fetch(`${API_BASE}/settings`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader()
      },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to update settings');
    return res.json();
  },

  // Demo Presets & Reset
  async getDemoCases() {
    const res = await fetch(`${API_BASE}/demo/cases`, {
      headers: getAuthHeader()
    });
    return res.json();
  },

  async triggerDemoCase(caseKey: string) {
    const res = await fetch(`${API_BASE}/demo/trigger/${caseKey}`, {
      method: 'POST',
      headers: getAuthHeader()
    });
    if (!res.ok) throw new Error('Failed to trigger demo case');
    return res.json();
  },

  async resetDemoDatabase() {
    const res = await fetch(`${API_BASE}/demo/reset`, {
      method: 'POST',
      headers: getAuthHeader()
    });
    if (!res.ok) throw new Error('Failed to reset demo database');
    return res.json();
  }
};
