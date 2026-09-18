from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict

# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"

class LoginRequest(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    email: str
    name: str
    role: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

# Extracted Field with Confidence and Location
class FieldValueConfidence(BaseModel):
    value: Any
    confidence: float = 1.0
    location: Optional[str] = None

class InvoiceItemSchema(BaseModel):
    description: str
    quantity: float
    unit_price: float
    discount: float = 0.0
    tax_rate: float = 0.0
    tax_amount: float = 0.0
    total_price: float
    confidence: float = 1.0

class ExtractedInvoiceData(BaseModel):
    invoice_number: FieldValueConfidence
    vendor_name: FieldValueConfidence
    vendor_address: Optional[FieldValueConfidence] = None
    vendor_email: Optional[FieldValueConfidence] = None
    vendor_tax_id: Optional[FieldValueConfidence] = None
    invoice_date: FieldValueConfidence
    due_date: Optional[FieldValueConfidence] = None
    po_number: Optional[FieldValueConfidence] = None
    currency: FieldValueConfidence = FieldValueConfidence(value="INR", confidence=1.0)
    payment_terms: Optional[FieldValueConfidence] = None
    subtotal: FieldValueConfidence
    discount: Optional[FieldValueConfidence] = None
    tax: FieldValueConfidence
    tax_percentage: Optional[FieldValueConfidence] = None
    total: FieldValueConfidence
    bank_account: Optional[FieldValueConfidence] = None
    bank_ifsc: Optional[FieldValueConfidence] = None
    line_items: list[InvoiceItemSchema] = []

# Validation Breakdown Schema
class ValidationOut(BaseModel):
    required_fields_status: str
    missing_fields: list[str] = []
    math_status: str
    calculated_subtotal: float
    calculated_total: float
    invoice_total: float
    math_difference: float
    math_notes: Optional[str] = None
    tax_status: str
    tax_type: str
    expected_tax_rate: float
    detected_tax_rate: float
    expected_tax_amount: float
    detected_tax_amount: float
    tax_difference: float
    tax_notes: Optional[str] = None
    po_match_status: str
    po_number: Optional[str] = None
    po_discrepancies: list[str] = []
    duplicate_status: str
    similarity_score: float
    matched_invoice_id: Optional[str] = None
    duplicate_notes: Optional[str] = None

# Risk Assessment Schema
class RiskAssessmentOut(BaseModel):
    risk_score: float
    risk_level: str
    duplicate_risk: bool
    unusual_amount_risk: bool
    unusual_tax_risk: bool
    repeat_invoice_num_risk: bool
    vendor_mismatch_risk: bool
    suspicious_bank_risk: bool
    abnormal_quantity_risk: bool
    price_anomaly_risk: bool
    weekend_pattern_risk: bool
    unusual_frequency_risk: bool
    modified_pattern_risk: bool
    missing_info_risk: bool
    anomalies_detected: list[dict[str, Any]] = []
    explanation: Optional[str] = None

# Tool Call and Agent Run Schemas
class AgentToolCallOut(BaseModel):
    id: int
    tool_name: str
    tool_arguments: dict[str, Any]
    tool_result: dict[str, Any]
    execution_time_ms: int
    status: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

class AgentRunOut(BaseModel):
    id: int
    agent_name: str
    status: str
    execution_time_ms: int
    retry_count: int
    input_data: Optional[dict[str, Any]] = None
    output_data: Optional[dict[str, Any]] = None
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    tool_calls: list[AgentToolCallOut] = []

    model_config = ConfigDict(from_attributes=True)

# Invoice Schemas
class InvoiceSummaryOut(BaseModel):
    id: int
    invoice_id: str
    invoice_number: Optional[str] = None
    vendor_name: Optional[str] = None
    invoice_date: Optional[str] = None
    currency: str = "INR"
    subtotal: float = 0.0
    tax_amount: float = 0.0
    total_amount: float = 0.0
    status: str
    final_decision: Optional[str] = None
    overall_confidence: float = 0.0
    risk_score: float = 0.0
    risk_level: str = "LOW"
    ai_recommendation: Optional[str] = None
    file_type: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class InvoiceDetailOut(InvoiceSummaryOut):
    original_filename: str
    file_path: str
    file_hash: Optional[str] = None
    due_date: Optional[str] = None
    payment_terms: Optional[str] = None
    discount: float = 0.0
    tax_percentage: float = 0.0
    bank_account_extracted: Optional[str] = None
    bank_ifsc_extracted: Optional[str] = None
    vendor_address_extracted: Optional[str] = None
    vendor_email_extracted: Optional[str] = None
    vendor_tax_id_extracted: Optional[str] = None
    reasoning_summary: Optional[str] = None
    decision_reasons: list[str] = []
    recommended_action: Optional[str] = None
    processing_time_ms: int = 0
    extracted_fields: Optional[dict[str, Any]] = None
    items: list[InvoiceItemSchema] = []
    validations: Optional[ValidationOut] = None
    risk_assessment: Optional[RiskAssessmentOut] = None
    agent_runs: list[AgentRunOut] = []

# Human-in-the-Loop Review
class ReviewActionRequest(BaseModel):
    decision: str # "APPROVE" or "REJECT"
    comments: Optional[str] = None
    reason: Optional[str] = None

class ReviewTaskOut(BaseModel):
    id: int
    invoice_id: int
    invoice_ref: str
    vendor_name: Optional[str] = None
    amount: float = 0.0
    status: str
    original_ai_decision: str
    ai_risk_score: float
    reason: Optional[str] = None
    human_decision: Optional[str] = None
    is_override: bool = False
    reviewer_comment: Optional[str] = None
    created_at: datetime
    reviewed_at: Optional[datetime] = None

# Vendor Schemas
class VendorOut(BaseModel):
    id: int
    vendor_code: str
    name: str
    tax_id: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    risk_level: str
    historical_avg_amount: float
    total_invoices_count: int
    bank_account: Optional[str] = None
    bank_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# Purchase Order Schemas
class POItemOut(BaseModel):
    id: int
    item_description: str
    quantity: float
    unit_price: float
    tax_rate: float
    total_price: float

    model_config = ConfigDict(from_attributes=True)

class PurchaseOrderOut(BaseModel):
    id: int
    po_number: str
    vendor_id: int
    vendor_name: Optional[str] = None
    order_date: datetime
    currency: str
    subtotal: float
    tax_amount: float
    total_amount: float
    status: str
    items: list[POItemOut] = []

    model_config = ConfigDict(from_attributes=True)

# Notification & Audit Schemas
class NotificationOut(BaseModel):
    id: int
    invoice_id: Optional[int] = None
    type: str
    title: str
    message: str
    severity: str
    is_read: bool
    action_url: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AuditLogOut(BaseModel):
    id: int
    actor_name: str
    actor_type: str
    action: str
    entity: str
    entity_id: Optional[str] = None
    result: str
    timestamp: datetime
    before_state: Optional[dict[str, Any]] = None
    after_state: Optional[dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)

# AI Assistant Schemas
class ChatMessage(BaseModel):
    role: str # "user" or "assistant" or "system"
    content: str
    invoice_id: Optional[str] = None

class ChatResponse(BaseModel):
    role: str = "assistant"
    content: str
    tools_used: list[str] = []
    referenced_invoices: list[str] = []
    confidence: float = 0.95

# Settings Schema
class SystemSettingsUpdate(BaseModel):
    confidence_auto_approve_min: Optional[float] = None
    confidence_review_min: Optional[float] = None
    risk_auto_approve_max: Optional[float] = None
    po_quantity_tolerance_pct: Optional[float] = None
    po_price_tolerance_pct: Optional[float] = None
    default_tax_rate: Optional[float] = None
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None
    llm_base_url: Optional[str] = None
