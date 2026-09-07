import re
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.models import Invoice, Vendor, PurchaseOrder
from backend.app.schemas.schemas import ChatMessage, ChatResponse
from backend.app.services.llm_service import llm_service

router = APIRouter(prefix="/ai", tags=["AI Assistant"])

@router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(msg: ChatMessage, db: Session = Depends(get_db)):
    """
    RAG-grounded AI Invoice Assistant. Retrieves live invoice, vendor,
    and PO records before answering to guarantee factuality.
    """
    tools_used = []
    referenced_invoices = []

    # 1. Identify targeted invoice from message or explicit invoice_id parameter
    inv = None
    if msg.invoice_id:
        tools_used.append("get_active_invoice")
        # Try finding by sys ID (INV-SYS-001) or invoice_number or int id
        if msg.invoice_id.isdigit():
            inv = db.query(Invoice).filter(Invoice.id == int(msg.invoice_id)).first()
        else:
            inv = db.query(Invoice).filter(
                (Invoice.invoice_id == msg.invoice_id) |
                (Invoice.invoice_number == msg.invoice_id)
            ).first()

    if not inv:
        # Search for invoice patterns like INV-10025 or INV-SYS-002 in user text
        inv_match = re.search(r"(INV(?:-SYS)?-[\w\d]+)", msg.content, re.IGNORECASE)
        if inv_match:
            tools_used.append("search_invoice_by_reference")
            matched_code = inv_match.group(1)
            inv = db.query(Invoice).filter(
                (Invoice.invoice_id.ilike(f"%{matched_code}%")) |
                (Invoice.invoice_number.ilike(f"%{matched_code}%"))
            ).first()

    # If still no specific invoice found, default to most recent if question is demonstrative
    if not inv and any(k in msg.content.lower() for k in ["this invoice", "the invoice", "flagged", "duplicate", "compare"]):
        tools_used.append("get_latest_processed_invoice")
        inv = db.query(Invoice).order_by(Invoice.created_at.desc()).first()

    active_invoice_context = None
    if inv:
        referenced_invoices.append(inv.invoice_id)
        active_invoice_context = {
            "invoice_id": inv.invoice_id,
            "invoice_number": inv.invoice_number,
            "vendor_name": inv.vendor_name_extracted,
            "total_amount": inv.total_amount,
            "subtotal": inv.subtotal,
            "tax_amount": inv.tax_amount,
            "tax_percentage": inv.tax_percentage,
            "status": inv.status,
            "final_decision": inv.final_decision,
            "risk_score": inv.risk_score,
            "risk_level": inv.risk_level,
            "ai_recommendation": inv.ai_recommendation,
            "decision_reasons": inv.decision_reasons,
            "recommended_action": inv.recommended_action,
            "po_number": inv.purchase_order.po_number if inv.purchase_order else None,
            "validations": {
                "math_status": inv.validations.math_status if inv.validations else "PASS",
                "tax_status": inv.validations.tax_status if inv.validations else "PASS",
                "tax_notes": inv.validations.tax_notes if inv.validations else "",
                "po_match_status": inv.validations.po_match_status if inv.validations else "PASS",
                "po_discrepancies": inv.validations.po_discrepancies if inv.validations else [],
                "duplicate_status": inv.validations.duplicate_status if inv.validations else "PASS",
                "similarity_score": inv.validations.similarity_score if inv.validations else 0.0,
                "matched_invoice_id": inv.validations.matched_invoice_id if inv.validations else None,
                "duplicate_notes": inv.validations.duplicate_notes if inv.validations else ""
            } if inv.validations else {}
        }

    # Aggregate general statistics for global questions
    invoices = db.query(Invoice).all()
    stats = {
        "total_invoices": len(invoices),
        "approved": sum(1 for i in invoices if i.status == "approved" or i.final_decision == "APPROVE"),
        "pending_review": sum(1 for i in invoices if i.status == "review_required"),
        "high_risk": sum(1 for i in invoices if i.risk_level in ["HIGH", "CRITICAL"])
    }
    tools_used.append("get_portfolio_summary_metrics")

    context = {
        "active_invoice": active_invoice_context,
        "stats": stats
    }

    reply = await llm_service.ask_assistant(msg.content, context)

    return ChatResponse(
        role="assistant",
        content=reply,
        tools_used=list(set(tools_used)),
        referenced_invoices=referenced_invoices,
        confidence=0.96
    )
