import time
from typing import Any
from sqlalchemy.orm import Session
from backend.app.models.models import Invoice, AgentRun, AgentToolCall
from backend.app.tools.agent_tools import create_review_task, send_notification
from backend.app.core.config import settings

class DecisionAgent:
    """
    Agent 10 — Decision & Routing Agent
    Responsibilities:
    - Apply confidence and risk routing matrix
    - Assign final system status: approved, review_required, rejected
    - Automatically dispatch Human-in-the-Loop review task if REVIEW required
    - Send real-time notification alerts
    - Record execution run and tool calls
    """
    name = "Decision Agent"

    def run(self, db: Session, invoice_id: int) -> dict[str, Any]:
        start_time = time.time()
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise ValueError(f"Invoice with ID {invoice_id} not found.")

        ai_rec = invoice.ai_recommendation or "REVIEW"
        confidence = invoice.overall_confidence or 0.0
        risk_score = invoice.risk_score or 0.0
        val = invoice.validations

        # Deterministic routing logic based on configurable thresholds
        decision = "REVIEW"
        routing_reason = ""

        # Auto-Approve rule
        if (
            confidence >= settings.CONFIDENCE_AUTO_APPROVE_MIN and
            risk_score <= settings.RISK_AUTO_APPROVE_MAX and
            val and val.math_status == "PASS" and
            val.required_fields_status == "PASS" and
            val.tax_status == "PASS" and
            val.duplicate_status == "PASS" and
            val.po_match_status in ["PASS", "NOT_FOUND"] and
            ai_rec == "APPROVE"
        ):
            decision = "APPROVE"
            invoice.status = "approved"
            routing_reason = "Passed all automated validation, tax, PO, and risk thresholds with high confidence."
        
        # Hard Reject rule (exact binary duplicate or severe missing info)
        elif val and (val.duplicate_status == "EXACT_DUPLICATE" or val.required_fields_status == "FAIL"):
            decision = "REJECT"
            invoice.status = "rejected"
            routing_reason = "Critical rule violation: exact binary duplicate or missing mandatory headers."
            
        # Human Review rule
        else:
            decision = "REVIEW"
            invoice.status = "review_required"
            routing_reason = "Discrepancy, elevated risk score, or moderate confidence requires human review."

        invoice.final_decision = decision
        db.commit()

        tool_calls_list = []

        # If REVIEW is required, dispatch review task
        if decision == "REVIEW":
            tool_start = time.time()
            task_res = create_review_task(
                db=db,
                invoice_id=invoice.id,
                original_ai_decision="REVIEW",
                ai_risk_score=risk_score,
                reason="; ".join(invoice.decision_reasons or [routing_reason])
            )
            tool_calls_list.append({
                "name": "create_review_task",
                "latency": int((time.time() - tool_start) * 1000),
                "args": {"invoice_id": invoice.id, "risk_score": risk_score},
                "result": task_res
            })

            # Send Notification
            tool_notif_start = time.time()
            notif_res = send_notification(
                db=db,
                title=f"Review Required: {invoice.invoice_number or invoice.invoice_id}",
                message=f"Invoice from {invoice.vendor_name_extracted} (₹{invoice.total_amount:,.2f}) flagged with Risk Score {risk_score:.0f}/100.",
                severity="WARNING" if risk_score < 75 else "CRITICAL",
                invoice_id=invoice.id
            )
            tool_calls_list.append({
                "name": "send_notification",
                "latency": int((time.time() - tool_notif_start) * 1000),
                "args": {"title": f"Review Required: {invoice.invoice_number}"},
                "result": notif_res
            })

        elif decision == "APPROVE":
            send_notification(
                db=db,
                title=f"Invoice Auto-Approved: {invoice.invoice_number or invoice.invoice_id}",
                message=f"Invoice from {invoice.vendor_name_extracted} (₹{invoice.total_amount:,.2f}) auto-approved for payment.",
                severity="SUCCESS",
                invoice_id=invoice.id
            )

        execution_time_ms = int((time.time() - start_time) * 1000)

        output_data = {
            "final_decision": decision,
            "status": invoice.status,
            "confidence": confidence,
            "risk_score": risk_score,
            "routing_reason": routing_reason
        }

        # Record Agent Run
        agent_run = AgentRun(
            invoice_id=invoice.id,
            agent_name=self.name,
            status="COMPLETED",
            execution_time_ms=execution_time_ms,
            input_data={"ai_recommendation": ai_rec, "risk_score": risk_score, "confidence": confidence},
            output_data=output_data
        )
        db.add(agent_run)
        db.commit()
        db.refresh(agent_run)

        for tc in tool_calls_list:
            tool_call = AgentToolCall(
                agent_run_id=agent_run.id,
                tool_name=tc["name"],
                tool_arguments=tc["args"],
                tool_result=tc["result"],
                execution_time_ms=tc["latency"],
                status="SUCCESS"
            )
            db.add(tool_call)
        db.commit()

        return output_data

decision_agent = DecisionAgent()
