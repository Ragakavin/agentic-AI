export interface User {
  id: number;
  email: string;
  name: string;
  role: 'admin' | 'finance_manager' | 'reviewer' | 'viewer';
  is_active: boolean;
}

export interface InvoiceItem {
  description: string;
  quantity: number;
  unit_price: number;
  discount: number;
  tax_rate: number;
  tax_amount: number;
  total_price: number;
  confidence: number;
}

export interface ValidationBreakdown {
  required_fields_status: 'PASS' | 'FAIL';
  missing_fields: string[];
  math_status: 'PASS' | 'MISMATCH';
  calculated_subtotal: number;
  calculated_total: number;
  invoice_total: number;
  math_difference: number;
  math_notes?: string;
  tax_status: 'PASS' | 'WARNING' | 'FAIL';
  tax_type: string;
  expected_tax_rate: number;
  detected_tax_rate: number;
  expected_tax_amount: number;
  detected_tax_amount: number;
  tax_difference: number;
  tax_notes?: string;
  po_match_status: 'PASS' | 'MISMATCH' | 'NOT_FOUND';
  po_number?: string;
  po_discrepancies: string[];
  duplicate_status: 'PASS' | 'POSSIBLE_DUPLICATE' | 'EXACT_DUPLICATE';
  similarity_score: number;
  matched_invoice_id?: string;
  duplicate_notes?: string;
}

export interface AnomalyItem {
  indicator: string;
  weight: number;
  detail: string;
}

export interface RiskAssessment {
  risk_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  duplicate_risk: boolean;
  unusual_amount_risk: boolean;
  unusual_tax_risk: boolean;
  repeat_invoice_num_risk: boolean;
  vendor_mismatch_risk: boolean;
  suspicious_bank_risk: boolean;
  abnormal_quantity_risk: boolean;
  price_anomaly_risk: boolean;
  weekend_pattern_risk: boolean;
  unusual_frequency_risk: boolean;
  modified_pattern_risk: boolean;
  missing_info_risk: boolean;
  anomalies_detected: AnomalyItem[];
  explanation?: string;
}

export interface AgentToolCall {
  id: number;
  tool_name: string;
  tool_arguments: Record<string, any>;
  tool_result: Record<string, any>;
  execution_time_ms: number;
  status: string;
  timestamp: string;
}

export interface AgentRun {
  id: number;
  agent_name: string;
  status: 'COMPLETED' | 'WARNING' | 'FAILED' | 'RUNNING';
  execution_time_ms: number;
  retry_count: number;
  input_data?: Record<string, any>;
  output_data?: Record<string, any>;
  error_message?: string;
  started_at: string;
  completed_at?: string;
  tool_calls: AgentToolCall[];
}

export interface InvoiceSummary {
  id: number;
  invoice_id: string;
  invoice_number?: string;
  vendor_name?: string;
  vendor_name_extracted?: string;
  invoice_date?: string;
  currency: string;
  subtotal: number;
  tax_amount: number;
  total_amount: number;
  status: 'received' | 'processing' | 'approved' | 'review_required' | 'rejected';
  final_decision?: 'APPROVE' | 'REVIEW' | 'REJECT';
  overall_confidence: number;
  risk_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  ai_recommendation?: string;
  file_type: string;
  created_at: string;
}

export interface InvoiceDetail extends InvoiceSummary {
  original_filename: string;
  file_path: string;
  file_hash?: string;
  due_date?: string;
  payment_terms?: string;
  discount: number;
  tax_percentage: number;
  bank_account_extracted?: string;
  bank_ifsc_extracted?: string;
  vendor_address_extracted?: string;
  vendor_email_extracted?: string;
  vendor_tax_id_extracted?: string;
  reasoning_summary?: string;
  decision_reasons: string[];
  recommended_action?: string;
  processing_time_ms: number;
  extracted_fields?: Record<string, any>;
  purchase_order?: { id: number; po_number: string };
  items: InvoiceItem[];
  validations?: ValidationBreakdown;
  risk_assessment?: RiskAssessment;
  agent_runs: AgentRun[];
}

export interface AgentOverview {
  name: string;
  role: string;
  status: 'ACTIVE' | 'WARNING' | 'IDLE' | 'FAILED';
  total_runs: number;
  avg_latency_ms: number;
  completed_count: number;
  warning_count: number;
  failed_count: number;
  total_tool_calls: number;
}

export interface Vendor {
  id: number;
  vendor_code: string;
  name: string;
  tax_id?: string;
  email?: string;
  phone?: string;
  address?: string;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  historical_avg_amount: number;
  total_invoices_count: number;
  bank_account?: string;
  bank_name?: string;
}

export interface POItem {
  id: number;
  item_description: string;
  quantity: number;
  unit_price: number;
  tax_rate: number;
  total_price: number;
}

export interface PurchaseOrder {
  id: number;
  po_number: string;
  vendor_id: number;
  vendor_name?: string;
  order_date: string;
  currency: string;
  subtotal: number;
  tax_amount: number;
  total_amount: number;
  status: string;
  items: POItem[];
}

export interface ReviewTask {
  id: number;
  invoice_id: number;
  invoice_ref: string;
  vendor_name?: string;
  amount: number;
  status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'RESOLVED';
  original_ai_decision: string;
  ai_risk_score: number;
  reason?: string;
  human_decision?: string;
  is_override: boolean;
  reviewer_comment?: string;
  created_at: string;
  reviewed_at?: string;
}

export interface NotificationItem {
  id: number;
  invoice_id?: number;
  type: string;
  title: string;
  message: string;
  severity: 'INFO' | 'WARNING' | 'CRITICAL' | 'SUCCESS';
  is_read: boolean;
  action_url?: string;
  created_at: string;
}

export interface AuditLogItem {
  id: number;
  actor_name: string;
  actor_type: string;
  action: string;
  entity: string;
  entity_id?: string;
  result: string;
  timestamp: string;
  before_state?: any;
  after_state?: any;
}

export interface AnalyticsData {
  kpis: {
    total_invoices: number;
    processed_invoices: number;
    approved: number;
    pending_review: number;
    rejected: number;
    high_risk: number;
    duplicates: number;
    avg_processing_time_ms: number;
  };
  charts: {
    approval_distribution: { name: string; value: number; color: string }[];
    risk_distribution: { level: string; count: number; color: string }[];
    vendor_spending: { vendor: string; amount: number }[];
    processing_trend: { month: string; invoices: number; approved: number; amount: number }[];
    confidence_distribution: { bucket: string; count: number }[];
    tax_distribution: { rate: string; count: number }[];
  };
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  tools_used?: string[];
  referenced_invoices?: string[];
}
