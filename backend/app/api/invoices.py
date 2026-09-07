import shutil
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.models import (
    Invoice, ReviewTask, AuditLog, User
)
from backend.app.schemas.schemas import (
    InvoiceSummaryOut, InvoiceDetailOut, ReviewActionRequest, ValidationOut,
    RiskAssessmentOut, AgentRunOut, InvoiceItemSchema
)
from backend.app.agents.intake_agent import intake_agent
from backend.app.agents.orchestrator import orchestrator
from backend.app.services.memory_service import memory_service
from backend.app.api.auth import get_current_user
from backend.app.core.config import settings

router = APIRouter(prefix="/invoices", tags=["Invoices"])

@router.post("/upload")
async def upload_invoice(
    file: UploadFile = File(...),
    auto_analyze: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Receive invoice document (PDF, PNG, JPG, etc.), run Intake Agent,
    and execute the full 10-stage Agentic AI processing cycle.
    """
    dest_path = settings.UPLOAD_DIR / file.filename
    try:
        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    try:
        intake_res = intake_agent.run(db, dest_path, file.filename)
        internal_id = intake_res["internal_db_id"]

        # Log User upload action
        audit = AuditLog(
            actor_name=current_user.name,
            actor_type="USER",
            action="INVOICE_UPLOAD",
            entity="invoice",
            entity_id=intake_res["invoice_id"],
            after_state={"filename": file.filename, "size": intake_res["file_size_bytes"]},
            result="SUCCESS"
        )
        db.add(audit)
        db.commit()

        if auto_analyze:
            process_res = await orchestrator.process_invoice(db, internal_id)
            return {
                "message": "Invoice uploaded and successfully processed by multi-agent system.",
                "intake": intake_res,
                "analysis": process_res
            }
        
        return {
            "message": "Invoice uploaded. Ready for agent analysis.",
            "intake": intake_res
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("", response_model=list[InvoiceSummaryOut])
def list_invoices(
    status: Optional[str] = None,
    risk_level: Optional[str] = None,
    vendor_id: Optional[int] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(Invoice)

    if status and status.lower() != "all":
        query = query.filter(Invoice.status == status.lower())
    if risk_level and risk_level.upper() != "ALL":
        query = query.filter(Invoice.risk_level == risk_level.upper())
    if vendor_id:
        query = query.filter(Invoice.vendor_id == vendor_id)
    if search:
        s = f"%{search}%"
        query = query.filter(
            (Invoice.invoice_id.ilike(s)) |
            (Invoice.invoice_number.ilike(s)) |
            (Invoice.vendor_name_extracted.ilike(s)) |
            (Invoice.original_filename.ilike(s))
        )

    invoices = query.order_by(Invoice.created_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for inv in invoices:
        result.append(InvoiceSummaryOut(
            id=inv.id,
            invoice_id=inv.invoice_id,
            invoice_number=inv.invoice_number,
            vendor_name=inv.vendor_name_extracted or (inv.vendor.name if inv.vendor else None),
            invoice_date=inv.invoice_date,
            currency=inv.currency,
            subtotal=inv.subtotal,
            tax_amount=inv.tax_amount,
            total_amount=inv.total_amount,
            status=inv.status,
            final_decision=inv.final_decision,
            overall_confidence=inv.overall_confidence,
            risk_score=inv.risk_score,
            risk_level=inv.risk_level,
            ai_recommendation=inv.ai_recommendation,
            file_type=inv.file_type,
            created_at=inv.created_at
        ))
    return result

@router.get("/{id}", response_model=InvoiceDetailOut)
def get_invoice_detail(id: int, db: Session = Depends(get_db)):
    inv = db.query(Invoice).filter(Invoice.id == id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")

    items_out = [
        InvoiceItemSchema(
            description=it.description,
            quantity=it.quantity,
            unit_price=it.unit_price,
            discount=it.discount,
            tax_rate=it.tax_rate,
            tax_amount=it.tax_amount,
            total_price=it.total_price,
            confidence=it.confidence
        )
        for it in inv.items
    ]

    val_out = None
    if inv.validations:
        v = inv.validations
        val_out = ValidationOut(
            required_fields_status=v.required_fields_status,
            missing_fields=v.missing_fields or [],
            math_status=v.math_status,
            calculated_subtotal=v.calculated_subtotal,
            calculated_total=v.calculated_total,
            invoice_total=v.invoice_total,
            math_difference=v.math_difference,
            math_notes=v.math_notes,
            tax_status=v.tax_status,
            tax_type=v.tax_type,
            expected_tax_rate=v.expected_tax_rate,
            detected_tax_rate=v.detected_tax_rate,
            expected_tax_amount=v.expected_tax_amount,
            detected_tax_amount=v.detected_tax_amount,
            tax_difference=v.tax_difference,
            tax_notes=v.tax_notes,
            po_match_status=v.po_match_status,
            po_number=v.po_number,
            po_discrepancies=v.po_discrepancies or [],
            duplicate_status=v.duplicate_status,
            similarity_score=v.similarity_score,
            matched_invoice_id=v.matched_invoice_id,
            duplicate_notes=v.duplicate_notes
        )

    risk_out = None
    if inv.risk_assessment:
        r = inv.risk_assessment
        risk_out = RiskAssessmentOut(
            risk_score=r.risk_score,
            risk_level=r.risk_level,
            duplicate_risk=r.duplicate_risk,
            unusual_amount_risk=r.unusual_amount_risk,
            unusual_tax_risk=r.unusual_tax_risk,
            repeat_invoice_num_risk=r.repeat_invoice_num_risk,
            vendor_mismatch_risk=r.vendor_mismatch_risk,
            suspicious_bank_risk=r.suspicious_bank_risk,
            abnormal_quantity_risk=r.abnormal_quantity_risk,
            price_anomaly_risk=r.price_anomaly_risk,
            weekend_pattern_risk=r.weekend_pattern_risk,
            unusual_frequency_risk=r.unusual_frequency_risk,
            modified_pattern_risk=r.modified_pattern_risk,
            missing_info_risk=r.missing_info_risk,
            anomalies_detected=r.anomalies_detected or [],
            explanation=r.explanation
        )

    runs_out = [
        AgentRunOut(
            id=run.id,
            agent_name=run.agent_name,
            status=run.status,
            execution_time_ms=run.execution_time_ms,
            retry_count=run.retry_count,
            input_data=run.input_data,
            output_data=run.output_data,
            error_message=run.error_message,
            started_at=run.started_at,
            completed_at=run.completed_at,
            tool_calls=[
                {
                    "id": tc.id,
                    "tool_name": tc.tool_name,
                    "tool_arguments": tc.tool_arguments,
                    "tool_result": tc.tool_result,
                    "execution_time_ms": tc.execution_time_ms,
                    "status": tc.status,
                    "timestamp": tc.timestamp
                }
                for tc in run.tool_calls
            ]
        )
        for run in inv.agent_runs
    ]

    return InvoiceDetailOut(
        id=inv.id,
        invoice_id=inv.invoice_id,
        invoice_number=inv.invoice_number,
        vendor_name=inv.vendor_name_extracted or (inv.vendor.name if inv.vendor else None),
        invoice_date=inv.invoice_date,
        due_date=inv.due_date,
        currency=inv.currency,
        payment_terms=inv.payment_terms,
        subtotal=inv.subtotal,
        discount=inv.discount,
        tax_amount=inv.tax_amount,
        tax_percentage=inv.tax_percentage,
        total_amount=inv.total_amount,
        bank_account_extracted=inv.bank_account_extracted,
        bank_ifsc_extracted=inv.bank_ifsc_extracted,
        vendor_address_extracted=inv.vendor_address_extracted,
        vendor_email_extracted=inv.vendor_email_extracted,
        vendor_tax_id_extracted=inv.vendor_tax_id_extracted,
        original_filename=inv.original_filename,
        file_path=inv.file_path,
        file_hash=inv.file_hash,
        file_type=inv.file_type,
        status=inv.status,
        final_decision=inv.final_decision,
        overall_confidence=inv.overall_confidence,
        risk_score=inv.risk_score,
        risk_level=inv.risk_level,
        ai_recommendation=inv.ai_recommendation,
        reasoning_summary=inv.reasoning_summary,
        decision_reasons=inv.decision_reasons or [],
        recommended_action=inv.recommended_action,
        processing_time_ms=inv.processing_time_ms,
        extracted_fields=inv.extracted_fields,
        items=items_out,
        validations=val_out,
        risk_assessment=risk_out,
        agent_runs=runs_out,
        created_at=inv.created_at
    )

@router.post("/{id}/analyze")
async def reanalyze_invoice(id: int, db: Session = Depends(get_db)):
    """Re-trigger the complete multi-agent analysis pipeline on an existing invoice."""
    inv = db.query(Invoice).filter(Invoice.id == id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    result = await orchestrator.process_invoice(db, inv.id)
    return {"message": "Agent analysis completed.", "analysis": result}

@router.post("/{id}/review")
def submit_human_review(
    id: int,
    req: ReviewActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Human-in-the-Loop Review: reviewer reviews AI recommendation,
    can Approve, Reject, or Override, providing justification.
    Stores human decision in long-term memory.
    """
    inv = db.query(Invoice).filter(Invoice.id == id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")

    decision = req.decision.upper()
    if decision not in ["APPROVE", "REJECT"]:
        raise HTTPException(status_code=400, detail="Decision must be 'APPROVE' or 'REJECT'")

    prev_status = inv.status
    prev_decision = inv.final_decision or inv.ai_recommendation

    is_override = (decision != inv.ai_recommendation)

    # Update Invoice Status
    inv.final_decision = decision
    inv.status = "approved" if decision == "APPROVE" else "rejected"

    # Update ReviewTask
    task = db.query(ReviewTask).filter(ReviewTask.invoice_id == inv.id).first()
    if task:
        task.status = "APPROVED" if decision == "APPROVE" else "REJECTED"
        task.assigned_to_user_id = current_user.id
        task.human_decision = decision
        task.is_override = is_override
        task.reviewer_comment = req.comments or req.reason
        task.reviewed_at = datetime.utcnow()

    # Record into Long-Term Memory (HumanFeedback)
    memory_service.record_human_override(
        db=db,
        invoice_id=inv.id,
        vendor_id=inv.vendor_id,
        original_ai_decision=inv.ai_recommendation or "REVIEW",
        human_decision=decision,
        reason=req.comments or req.reason or "Approved by human reviewer",
        context={
            "risk_score": inv.risk_score,
            "discrepancies": inv.validations.po_discrepancies if inv.validations else []
        }
    )

    # Record in Audit Trail
    audit = AuditLog(
        actor_name=current_user.name,
        actor_type="USER",
        action="HUMAN_REVIEW_DECISION",
        entity="invoice",
        entity_id=inv.invoice_id,
        before_state={"status": prev_status, "decision": prev_decision},
        after_state={"status": inv.status, "decision": decision, "override": is_override, "comments": req.comments},
        result="SUCCESS"
    )
    db.add(audit)
    db.commit()

    return {
        "message": f"Invoice successfully marked as {decision}.",
        "invoice_id": inv.invoice_id,
        "final_decision": decision,
        "is_override": is_override
    }
