import time
import hashlib
from difflib import SequenceMatcher
from datetime import datetime
from typing import Any, Callable, Optional
from sqlalchemy.orm import Session
from backend.app.models.models import (
    Vendor, PurchaseOrder, Invoice, ReviewTask, Notification, AgentToolCall
)
from backend.app.core.config import settings

class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, dict[str, Any]] = {}

    def register(self, name: str, description: str, parameters: dict[str, Any]):
        def decorator(func: Callable):
            self._tools[name] = {
                "name": name,
                "description": description,
                "parameters": parameters,
                "func": func
            }
            return func
        return decorator

    def get_tool(self, name: str) -> Optional[dict[str, Any]]:
        return self._tools.get(name)

    def list_tools(self) -> list[dict[str, Any]]:
        return [
            {
                "name": t["name"],
                "description": t["description"],
                "parameters": t["parameters"]
            }
            for t in self._tools.values()
        ]

tool_registry = ToolRegistry()

# ----------------- Dynamic Tool Definitions ----------------- #

@tool_registry.register(
    name="calculate_invoice_total",
    description="Calculate line item sums and verify total mathematically: Subtotal - Discount + Tax = Total.",
    parameters={
        "type": "object",
        "properties": {
            "subtotal": {"type": "number"},
            "discount": {"type": "number"},
            "tax": {"type": "number"},
            "invoice_total": {"type": "number"}
        },
        "required": ["subtotal", "tax", "invoice_total"]
    }
)
def calculate_invoice_total(subtotal: float, tax: float, invoice_total: float, discount: float = 0.0) -> dict[str, Any]:
    calculated = round(subtotal - discount + tax, 2)
    invoice_total_rounded = round(invoice_total, 2)
    diff = round(abs(calculated - invoice_total_rounded), 2)
    is_match = diff <= 1.0  # Allow minor rounding penny tolerance
    
    return {
        "status": "PASS" if is_match else "MISMATCH",
        "calculated_total": calculated,
        "invoice_total": invoice_total_rounded,
        "difference": diff,
        "notes": "Calculations match." if is_match else f"Total discrepancy of ₹{diff:,.2f} detected."
    }

@tool_registry.register(
    name="validate_tax",
    description="Analyze GST/VAT percentages, compute expected tax vs invoice tax, and verify tax compliance.",
    parameters={
        "type": "object",
        "properties": {
            "subtotal": {"type": "number"},
            "tax_amount": {"type": "number"},
            "tax_percentage": {"type": "number"},
            "expected_rate": {"type": "number"}
        },
        "required": ["subtotal", "tax_amount"]
    }
)
def validate_tax(subtotal: float, tax_amount: float, tax_percentage: Optional[float] = None, expected_rate: float = 18.0) -> dict[str, Any]:
    expected_tax = round((subtotal * expected_rate) / 100.0, 2)
    actual_tax = round(tax_amount, 2)
    diff = round(abs(expected_tax - actual_tax), 2)
    
    # Calculate effective rate if not supplied
    effective_rate = round((actual_tax / subtotal) * 100.0, 1) if subtotal > 0 else 0.0
    detected_rate = tax_percentage if (tax_percentage is not None and tax_percentage > 0) else effective_rate
    
    # Check against valid tax rates in system
    is_rate_valid = any(abs(detected_rate - r) < 0.5 for r in settings.VALID_TAX_RATES)
    is_expected = abs(detected_rate - expected_rate) < 0.5
    
    if not is_rate_valid or not is_expected:
        status = "FAIL" if abs(detected_rate - expected_rate) >= 5.0 else "WARNING"
        notes = f"Tax rate {detected_rate}% deviates from expected rule of {expected_rate}%."
    else:
        status = "PASS"
        notes = f"Tax rate complies with {expected_rate}% rule."

    return {
        "tax_status": status,
        "tax_type": "GST (CGST/SGST/IGST)",
        "expected_tax_rate": expected_rate,
        "detected_tax_rate": detected_rate,
        "expected_tax_amount": expected_tax,
        "detected_tax_amount": actual_tax,
        "tax_difference": diff,
        "tax_notes": notes
    }

@tool_registry.register(
    name="search_duplicate_invoice",
    description="Perform fuzzy matching and document hash comparison against historical invoice database.",
    parameters={
        "type": "object",
        "properties": {
            "invoice_number": {"type": "string"},
            "vendor_name": {"type": "string"},
            "amount": {"type": "number"},
            "doc_hash": {"type": "string"},
            "exclude_id": {"type": "integer"}
        },
        "required": ["invoice_number", "vendor_name"]
    }
)
def search_duplicate_invoice(
    db: Session,
    invoice_number: str,
    vendor_name: str,
    amount: float,
    doc_hash: Optional[str] = None,
    exclude_id: Optional[int] = None
) -> dict[str, Any]:
    query = db.query(Invoice)
    if exclude_id:
        query = query.filter(Invoice.id != exclude_id)
        
    candidates = query.all()
    highest_sim = 0.0
    matched_inv = None
    duplicate_type = "NONE"

    for cand in candidates:
        # Check exact hash match
        if doc_hash and cand.file_hash and cand.file_hash == doc_hash:
            return {
                "duplicate_status": "EXACT_DUPLICATE",
                "similarity_score": 1.0,
                "matched_invoice_id": cand.invoice_id,
                "notes": f"Exact binary document hash match found with invoice {cand.invoice_id}."
            }

        # Check invoice number similarity
        clean_cand_num = "".join(filter(str.isalnum, (cand.invoice_number or "").lower()))
        clean_inv_num = "".join(filter(str.isalnum, (invoice_number or "").lower()))
        
        num_sim = SequenceMatcher(None, clean_cand_num, clean_inv_num).ratio() if clean_cand_num else 0.0
        
        # Vendor similarity
        cand_vendor = (cand.vendor_name_extracted or (cand.vendor.name if cand.vendor else "")).lower()
        curr_vendor = (vendor_name or "").lower()
        vendor_sim = SequenceMatcher(None, cand_vendor, curr_vendor).ratio() if cand_vendor else 0.0
        
        # Amount match
        amount_match = abs((cand.total_amount or 0.0) - amount) < 1.0

        # Weighted aggregate similarity
        agg_sim = (num_sim * 0.45) + (vendor_sim * 0.35) + (0.20 if amount_match else 0.0)
        
        if agg_sim > highest_sim:
            highest_sim = agg_sim
            matched_inv = cand

    if highest_sim >= 0.85:
        duplicate_type = "POSSIBLE_DUPLICATE"
        notes = f"High similarity ({highest_sim*100:.1f}%) detected with prior invoice {matched_inv.invoice_id} ({matched_inv.invoice_number})."
    else:
        duplicate_type = "PASS"
        notes = "No duplicate invoices detected in system database."

    return {
        "duplicate_status": duplicate_type,
        "similarity_score": round(highest_sim, 2),
        "matched_invoice_id": matched_inv.invoice_id if matched_inv else None,
        "notes": notes
    }

@tool_registry.register(
    name="get_vendor",
    description="Retrieve vendor profile, verified tax ID, and historical spending average.",
    parameters={
        "type": "object",
        "properties": {
            "vendor_name": {"type": "string"},
            "vendor_id": {"type": "integer"}
        }
    }
)
def get_vendor(db: Session, vendor_name: Optional[str] = None, vendor_id: Optional[int] = None) -> Optional[dict[str, Any]]:
    vendor = None
    if vendor_id:
        vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    elif vendor_name:
        # Fuzzy match vendor
        vendors = db.query(Vendor).all()
        best_score = 0.0
        for v in vendors:
            sim = SequenceMatcher(None, v.name.lower(), vendor_name.lower()).ratio()
            if sim > best_score and sim >= 0.60:
                best_score = sim
                vendor = v
                
    if not vendor:
        return None

    return {
        "id": vendor.id,
        "vendor_code": vendor.vendor_code,
        "name": vendor.name,
        "tax_id": vendor.tax_id,
        "risk_level": vendor.risk_level,
        "historical_avg_amount": vendor.historical_avg_amount,
        "total_invoices_count": vendor.total_invoices_count,
        "bank_account": vendor.bank_account
    }

@tool_registry.register(
    name="get_purchase_order",
    description="Retrieve purchase order and line items for three-way matching.",
    parameters={
        "type": "object",
        "properties": {
            "po_number": {"type": "string"}
        },
        "required": ["po_number"]
    }
)
def get_purchase_order(db: Session, po_number: str) -> Optional[dict[str, Any]]:
    po = db.query(PurchaseOrder).filter(PurchaseOrder.po_number.ilike(f"%{po_number.strip()}%")).first()
    if not po:
        return None

    items = [
        {
            "id": it.id,
            "description": it.item_description,
            "quantity": it.quantity,
            "unit_price": it.unit_price,
            "tax_rate": it.tax_rate,
            "total_price": it.total_price
        }
        for it in po.items
    ]

    return {
        "id": po.id,
        "po_number": po.po_number,
        "vendor_id": po.vendor_id,
        "vendor_name": po.vendor.name if po.vendor else None,
        "subtotal": po.subtotal,
        "tax_amount": po.tax_amount,
        "total_amount": po.total_amount,
        "status": po.status,
        "items": items
    }

@tool_registry.register(
    name="compare_invoice_with_po",
    description="Compare invoice line items against purchase order with configurable quantity and price tolerances.",
    parameters={
        "type": "object",
        "properties": {
            "invoice_items": {"type": "array"},
            "po_items": {"type": "array"},
            "invoice_total": {"type": "number"},
            "po_total": {"type": "number"}
        },
        "required": ["invoice_items", "po_items"]
    }
)
def compare_invoice_with_po(
    invoice_items: list[dict[str, Any]],
    po_items: list[dict[str, Any]],
    invoice_total: float,
    po_total: float,
    qty_tolerance_pct: float = 5.0,
    price_tolerance_pct: float = 3.0
) -> dict[str, Any]:
    discrepancies = []
    
    # Compare totals
    tot_diff_pct = abs(invoice_total - po_total) / po_total * 100 if po_total > 0 else 0
    if tot_diff_pct > max(qty_tolerance_pct, price_tolerance_pct):
        discrepancies.append(f"Total amount difference: Invoice ₹{invoice_total:,.2f} vs PO ₹{po_total:,.2f} ({tot_diff_pct:.1f}% diff)")

    # Compare line items
    for inv_item in invoice_items:
        inv_desc = inv_item.get("description", "").lower()
        inv_qty = inv_item.get("quantity", 0)
        inv_price = inv_item.get("unit_price", 0)
        
        # Find closest match in PO items
        matched_po_item = None
        best_sim = 0.0
        for po_item in po_items:
            sim = SequenceMatcher(None, inv_desc, po_item.get("description", "").lower()).ratio()
            if sim > best_sim:
                best_sim = sim
                matched_po_item = po_item
                
        if matched_po_item and best_sim >= 0.50:
            po_qty = matched_po_item.get("quantity", 0)
            po_price = matched_po_item.get("unit_price", 0)
            
            # Check quantity tolerance
            qty_diff = inv_qty - po_qty
            qty_diff_pct = abs(qty_diff) / po_qty * 100 if po_qty > 0 else 0
            if qty_diff > 0 and qty_diff_pct > qty_tolerance_pct:
                discrepancies.append(
                    f"Line '{inv_item.get('description')}': Invoice Qty {inv_qty} exceeds PO Qty {po_qty} by +{qty_diff:g} ({qty_diff_pct:.1f}% diff, tolerance is {qty_tolerance_pct}%)"
                )

            # Check unit price tolerance
            price_diff = inv_price - po_price
            price_diff_pct = abs(price_diff) / po_price * 100 if po_price > 0 else 0
            if price_diff > 0 and price_diff_pct > price_tolerance_pct:
                discrepancies.append(
                    f"Line '{inv_item.get('description')}': Invoice Price ₹{inv_price:,.2f} exceeds PO Price ₹{po_price:,.2f} by +₹{price_diff:,.2f} ({price_diff_pct:.1f}% diff)"
                )
        else:
            discrepancies.append(f"Line item '{inv_item.get('description')}' was not found in Purchase Order specification.")

    status = "PASS" if not discrepancies else "MISMATCH"
    return {
        "po_match_status": status,
        "po_discrepancies": discrepancies,
        "matched_items_count": len(invoice_items),
        "tolerance_used": {"quantity_pct": qty_tolerance_pct, "price_pct": price_tolerance_pct}
    }

@tool_registry.register(
    name="calculate_risk_score",
    description="Evaluate 12 fraud and anomaly detection indicators and produce consolidated Risk Score (0-100).",
    parameters={
        "type": "object",
        "properties": {
            "anomalies": {"type": "object"}
        },
        "required": ["anomalies"]
    }
)
def calculate_risk_score(anomalies: dict[str, bool], anomaly_details: Optional[dict[str, str]] = None) -> dict[str, Any]:
    weights = {
        "duplicate_risk": 40.0,
        "unusual_amount_risk": 20.0,
        "unusual_tax_risk": 25.0,
        "repeat_invoice_num_risk": 30.0,
        "vendor_mismatch_risk": 25.0,
        "suspicious_bank_risk": 30.0,
        "abnormal_quantity_risk": 20.0,
        "price_anomaly_risk": 15.0,
        "weekend_pattern_risk": 10.0,
        "unusual_frequency_risk": 15.0,
        "modified_pattern_risk": 35.0,
        "missing_info_risk": 20.0,
    }

    raw_score = 0.0
    detected_list = []
    
    for indicator, is_triggered in anomalies.items():
        if is_triggered:
            wt = weights.get(indicator, 10.0)
            raw_score += wt
            detected_list.append({
                "indicator": indicator,
                "weight": wt,
                "detail": (anomaly_details or {}).get(indicator, f"Anomaly flagged: {indicator}")
            })

    # Normalized risk score between 0 and 100
    final_score = min(100.0, max(0.0, round(raw_score, 1)))

    if final_score <= 30.0:
        level = "LOW"
    elif final_score <= 60.0:
        level = "MEDIUM"
    elif final_score <= 80.0:
        level = "HIGH"
    else:
        level = "CRITICAL"

    explanation = "Potential risk detected — human review recommended." if final_score > 30.0 else "Low risk profile — all parameters within standard bounds."

    return {
        "risk_score": final_score,
        "risk_level": level,
        "detected_anomalies": detected_list,
        "explanation": explanation
    }

@tool_registry.register(
    name="create_review_task",
    description="Generate a Human-in-the-Loop review task in the Accounts Payable queue.",
    parameters={
        "type": "object",
        "properties": {
            "invoice_id": {"type": "integer"},
            "original_ai_decision": {"type": "string"},
            "ai_risk_score": {"type": "number"},
            "reason": {"type": "string"}
        },
        "required": ["invoice_id", "original_ai_decision"]
    }
)
def create_review_task(
    db: Session,
    invoice_id: int,
    original_ai_decision: str,
    ai_risk_score: float,
    reason: str
) -> dict[str, Any]:
    # Check if task already exists
    existing = db.query(ReviewTask).filter(ReviewTask.invoice_id == invoice_id).first()
    if existing:
        return {"status": "EXISTS", "task_id": existing.id}

    task = ReviewTask(
        invoice_id=invoice_id,
        status="PENDING",
        original_ai_decision=original_ai_decision,
        ai_risk_score=ai_risk_score,
        reason=reason
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return {"status": "CREATED", "task_id": task.id}

@tool_registry.register(
    name="send_notification",
    description="Dispatch an in-app alert notification to Accounts Payable finance users.",
    parameters={
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "message": {"type": "string"},
            "severity": {"type": "string"},
            "invoice_id": {"type": "integer"}
        },
        "required": ["title", "message"]
    }
)
def send_notification(
    db: Session,
    title: str,
    message: str,
    severity: str = "INFO",
    invoice_id: Optional[int] = None,
    action_url: Optional[str] = None
) -> dict[str, Any]:
    notif = Notification(
        invoice_id=invoice_id,
        type=severity,
        title=title,
        message=message,
        severity=severity,
        action_url=action_url or (f"/invoices/{invoice_id}" if invoice_id else None)
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return {"status": "SENT", "notification_id": notif.id}
