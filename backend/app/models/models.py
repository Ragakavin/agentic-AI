from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
)
from sqlalchemy.orm import relationship
from backend.app.database.session import Base

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False) # 'admin', 'finance_manager', 'reviewer', 'viewer'
    description = Column(String(255), nullable=True)
    
    users = relationship("User", back_populates="role")


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(120), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    role = relationship("Role", back_populates="users")
    review_tasks = relationship("ReviewTask", back_populates="reviewer")


class Vendor(Base):
    __tablename__ = "vendors"
    
    id = Column(Integer, primary_key=True, index=True)
    vendor_code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(150), index=True, nullable=False)
    tax_id = Column(String(50), nullable=True)
    email = Column(String(100), nullable=True)
    phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    risk_level = Column(String(20), default="LOW") # LOW, MEDIUM, HIGH
    historical_avg_amount = Column(Float, default=0.0)
    total_invoices_count = Column(Integer, default=0)
    bank_account = Column(String(100), nullable=True)
    bank_name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    invoices = relationship("Invoice", back_populates="vendor")
    purchase_orders = relationship("PurchaseOrder", back_populates="vendor")


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    po_number = Column(String(50), unique=True, index=True, nullable=False)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    order_date = Column(DateTime, default=datetime.utcnow)
    currency = Column(String(10), default="INR")
    subtotal = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    status = Column(String(30), default="OPEN") # OPEN, MATCHED, PARTIAL, CLOSED
    created_at = Column(DateTime, default=datetime.utcnow)
    
    vendor = relationship("Vendor", back_populates="purchase_orders")
    items = relationship("PurchaseOrderItem", back_populates="purchase_order", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="purchase_order")


class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    po_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False)
    item_description = Column(String(255), nullable=False)
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    tax_rate = Column(Float, default=18.0)
    total_price = Column(Float, nullable=False)
    
    purchase_order = relationship("PurchaseOrder", back_populates="items")


class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(String(50), unique=True, index=True, nullable=False) # e.g. INV-SYS-001
    invoice_number = Column(String(50), index=True, nullable=True) # Extracted invoice # e.g. INV-10025
    original_filename = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False) # PDF, PNG, JPG, etc.
    file_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer, default=0)
    file_hash = Column(String(64), index=True, nullable=True) # SHA-256
    
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=True)
    po_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=True)
    
    vendor_name_extracted = Column(String(150), nullable=True)
    vendor_address_extracted = Column(Text, nullable=True)
    vendor_email_extracted = Column(String(100), nullable=True)
    vendor_tax_id_extracted = Column(String(50), nullable=True)
    
    invoice_date = Column(String(30), nullable=True)
    due_date = Column(String(30), nullable=True)
    currency = Column(String(10), default="INR")
    payment_terms = Column(String(50), nullable=True)
    
    subtotal = Column(Float, default=0.0)
    discount = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    tax_percentage = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    
    bank_account_extracted = Column(String(100), nullable=True)
    bank_ifsc_extracted = Column(String(50), nullable=True)
    
    # Status & Agent Decisions
    status = Column(String(30), default="received") # received, processing, approved, review_required, rejected
    final_decision = Column(String(30), nullable=True) # APPROVE, REVIEW, REJECT
    overall_confidence = Column(Float, default=0.0)
    risk_score = Column(Float, default=0.0)
    risk_level = Column(String(20), default="LOW") # LOW, MEDIUM, HIGH, CRITICAL
    
    # Reasoning & Explainability
    ai_recommendation = Column(String(30), nullable=True)
    reasoning_summary = Column(Text, nullable=True)
    decision_reasons = Column(JSON, default=list) # List of strings
    recommended_action = Column(Text, nullable=True)
    processing_time_ms = Column(Integer, default=0)
    
    # Metadata and extraction raw results
    extracted_fields = Column(JSON, default=dict)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    vendor = relationship("Vendor", back_populates="invoices")
    purchase_order = relationship("PurchaseOrder", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    validations = relationship("InvoiceValidation", back_populates="invoice", uselist=False, cascade="all, delete-orphan")
    risk_assessment = relationship("RiskAssessment", back_populates="invoice", uselist=False, cascade="all, delete-orphan")
    agent_runs = relationship("AgentRun", back_populates="invoice", cascade="all, delete-orphan")
    review_tasks = relationship("ReviewTask", back_populates="invoice", cascade="all, delete-orphan")
    reports = relationship("InvoiceReport", back_populates="invoice", cascade="all, delete-orphan")


class InvoiceItem(Base):
    __tablename__ = "invoice_items"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    description = Column(String(255), nullable=False)
    quantity = Column(Float, default=1.0)
    unit_price = Column(Float, default=0.0)
    discount = Column(Float, default=0.0)
    tax_rate = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    total_price = Column(Float, default=0.0)
    confidence = Column(Float, default=1.0)
    
    invoice = relationship("Invoice", back_populates="items")


class InvoiceValidation(Base):
    __tablename__ = "invoice_validations"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), unique=True, nullable=False)
    
    # Required Fields
    required_fields_status = Column(String(20), default="PASS") # PASS, FAIL
    missing_fields = Column(JSON, default=list)
    
    # Mathematical Validation
    math_status = Column(String(20), default="PASS") # PASS, MISMATCH
    calculated_subtotal = Column(Float, default=0.0)
    calculated_total = Column(Float, default=0.0)
    invoice_total = Column(Float, default=0.0)
    math_difference = Column(Float, default=0.0)
    math_notes = Column(Text, nullable=True)
    
    # Tax Validation
    tax_status = Column(String(20), default="PASS") # PASS, WARNING, FAIL
    tax_type = Column(String(50), default="GST") # GST, CGST+SGST, IGST, VAT
    expected_tax_rate = Column(Float, default=18.0)
    detected_tax_rate = Column(Float, default=18.0)
    expected_tax_amount = Column(Float, default=0.0)
    detected_tax_amount = Column(Float, default=0.0)
    tax_difference = Column(Float, default=0.0)
    tax_notes = Column(Text, nullable=True)
    
    # PO Match Validation
    po_match_status = Column(String(20), default="PASS") # PASS, MISMATCH, NOT_FOUND
    po_number = Column(String(50), nullable=True)
    po_discrepancies = Column(JSON, default=list)
    
    # Duplicate Validation
    duplicate_status = Column(String(20), default="PASS") # PASS, POSSIBLE_DUPLICATE, EXACT_DUPLICATE
    similarity_score = Column(Float, default=0.0)
    matched_invoice_id = Column(String(50), nullable=True)
    duplicate_notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    invoice = relationship("Invoice", back_populates="validations")


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), unique=True, nullable=False)
    
    risk_score = Column(Float, default=0.0) # 0 to 100
    risk_level = Column(String(20), default="LOW") # LOW, MEDIUM, HIGH, CRITICAL
    
    # 12 specific anomaly detector results
    duplicate_risk = Column(Boolean, default=False)
    unusual_amount_risk = Column(Boolean, default=False)
    unusual_tax_risk = Column(Boolean, default=False)
    repeat_invoice_num_risk = Column(Boolean, default=False)
    vendor_mismatch_risk = Column(Boolean, default=False)
    suspicious_bank_risk = Column(Boolean, default=False)
    abnormal_quantity_risk = Column(Boolean, default=False)
    price_anomaly_risk = Column(Boolean, default=False)
    weekend_pattern_risk = Column(Boolean, default=False)
    unusual_frequency_risk = Column(Boolean, default=False)
    modified_pattern_risk = Column(Boolean, default=False)
    missing_info_risk = Column(Boolean, default=False)
    
    anomalies_detected = Column(JSON, default=list) # Detailed breakdown of all triggered anomalies
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    invoice = relationship("Invoice", back_populates="risk_assessment")


class AgentRun(Base):
    __tablename__ = "agent_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    agent_name = Column(String(100), nullable=False)
    status = Column(String(30), default="COMPLETED") # RUNNING, COMPLETED, WARNING, FAILED
    execution_time_ms = Column(Integer, default=0)
    retry_count = Column(Integer, default=0)
    input_data = Column(JSON, default=dict)
    output_data = Column(JSON, default=dict)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    invoice = relationship("Invoice", back_populates="agent_runs")
    tool_calls = relationship("AgentToolCall", back_populates="agent_run", cascade="all, delete-orphan")


class AgentToolCall(Base):
    __tablename__ = "agent_tool_calls"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_run_id = Column(Integer, ForeignKey("agent_runs.id"), nullable=False)
    tool_name = Column(String(100), nullable=False)
    tool_arguments = Column(JSON, default=dict)
    tool_result = Column(JSON, default=dict)
    execution_time_ms = Column(Integer, default=0)
    status = Column(String(20), default="SUCCESS")
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    agent_run = relationship("AgentRun", back_populates="tool_calls")


class ReviewTask(Base):
    __tablename__ = "review_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    assigned_to_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String(30), default="PENDING") # PENDING, APPROVED, REJECTED, RESOLVED
    
    original_ai_decision = Column(String(30), nullable=False)
    ai_risk_score = Column(Float, default=0.0)
    reason = Column(Text, nullable=True)
    
    human_decision = Column(String(30), nullable=True) # APPROVE, REJECT
    is_override = Column(Boolean, default=False)
    reviewer_comment = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    invoice = relationship("Invoice", back_populates="review_tasks")
    reviewer = relationship("User", back_populates="review_tasks")


class HumanFeedback(Base):
    __tablename__ = "human_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=True)
    original_ai_decision = Column(String(30), nullable=False)
    human_decision = Column(String(30), nullable=False)
    reason_given = Column(Text, nullable=True)
    feedback_context = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)


class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True)
    type = Column(String(50), nullable=False) # HIGH_RISK, DUPLICATE, REVIEW_REQUIRED, APPROVED, REJECTED
    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String(20), default="INFO") # INFO, WARNING, CRITICAL, SUCCESS
    is_read = Column(Boolean, default=False)
    action_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    actor_name = Column(String(100), nullable=False) # User name or Agent name
    actor_type = Column(String(30), nullable=False) # USER or AGENT
    action = Column(String(100), nullable=False)
    entity = Column(String(50), nullable=False) # invoice, vendor, po, setting
    entity_id = Column(String(50), nullable=True)
    before_state = Column(JSON, nullable=True)
    after_state = Column(JSON, nullable=True)
    result = Column(String(30), default="SUCCESS")
    timestamp = Column(DateTime, default=datetime.utcnow)


class InvoiceReport(Base):
    __tablename__ = "invoice_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    report_type = Column(String(20), default="PDF") # PDF, EXCEL, CSV
    file_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    invoice = relationship("Invoice", back_populates="reports")


class SystemSetting(Base):
    __tablename__ = "system_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(JSON, nullable=False)
    description = Column(String(255), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
