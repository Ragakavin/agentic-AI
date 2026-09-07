import time
import logging
from typing import Any
from sqlalchemy.orm import Session
from backend.app.models.models import Invoice, AuditLog
from backend.app.agents.extraction_agent import extraction_agent
from backend.app.agents.validation_agent import validation_agent
from backend.app.agents.tax_agent import tax_agent
from backend.app.agents.duplicate_agent import duplicate_agent
from backend.app.agents.po_agent import po_matching_agent
from backend.app.agents.vendor_agent import vendor_verification_agent
from backend.app.agents.fraud_agent import fraud_detection_agent
from backend.app.agents.reasoning_agent import reasoning_agent
from backend.app.agents.decision_agent import decision_agent
from backend.app.services.memory_service import memory_service

logger = logging.getLogger("InvoiceAgentOrchestrator")

class InvoiceAgentOrchestrator:
    """
    Agent Orchestrator
    Implements the complete cycle:
    Observe → Understand → Extract → Validate → Reason → Use Tools → Make Decision → Take Action → Learn/Remember → Report
    """

    async def process_invoice(self, db: Session, invoice_id: int) -> dict[str, Any]:
        start_time = time.time()
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise ValueError(f"Invoice {invoice_id} not found.")

        invoice.status = "processing"
        db.commit()

        # Initialize short-term memory
        memory_service.init_session(invoice.invoice_id, {
            "invoice_id": invoice.invoice_id,
            "filename": invoice.original_filename,
            "file_type": invoice.file_type
        })

        # Record start in Audit Trail
        self._log_audit(db, "System Orchestrator", "AGENT", "PIPELINE_START", "invoice", invoice.invoice_id, None, {"status": "processing"})

        try:
            # Stage 1: Extraction Agent
            logger.info(f"Stage 1: Running Extraction Agent on invoice {invoice.invoice_id}")
            extracted = extraction_agent.run(db, invoice.id)
            memory_service.update_session(invoice.invoice_id, "EXTRACTION", extracted)

            # Stage 2: Vendor Verification Agent
            logger.info(f"Stage 2: Running Vendor Verification on invoice {invoice.invoice_id}")
            vendor_res = vendor_verification_agent.run(db, invoice.id)
            memory_service.update_session(invoice.invoice_id, "VENDOR", vendor_res)

            # Stage 3: PO Matching Agent
            logger.info(f"Stage 3: Running PO Matching on invoice {invoice.invoice_id}")
            po_res = po_matching_agent.run(db, invoice.id)
            memory_service.update_session(invoice.invoice_id, "PO_MATCHING", po_res)

            # Stage 4: Mathematical Validation Agent
            logger.info(f"Stage 4: Running Validation on invoice {invoice.invoice_id}")
            val_res = validation_agent.run(db, invoice.id)
            memory_service.update_session(invoice.invoice_id, "VALIDATION", val_res)

            # Stage 5: Tax Validation Agent
            logger.info(f"Stage 5: Running Tax Validation on invoice {invoice.invoice_id}")
            tax_res = tax_agent.run(db, invoice.id)
            memory_service.update_session(invoice.invoice_id, "TAX", tax_res)

            # Stage 6: Duplicate Detection Agent
            logger.info(f"Stage 6: Running Duplicate Detection on invoice {invoice.invoice_id}")
            dup_res = duplicate_agent.run(db, invoice.id)
            memory_service.update_session(invoice.invoice_id, "DUPLICATE", dup_res)

            # Stage 7: Fraud & Anomaly Detection Agent
            logger.info(f"Stage 7: Running Fraud Detection on invoice {invoice.invoice_id}")
            fraud_res = fraud_detection_agent.run(db, invoice.id)
            memory_service.update_session(invoice.invoice_id, "FRAUD", fraud_res)

            # Stage 8: AI Reasoning Agent (with LLM and multi-agent synthesis)
            logger.info(f"Stage 8: Running AI Reasoning Agent on invoice {invoice.invoice_id}")
            reason_res = await reasoning_agent.run(db, invoice.id)
            memory_service.update_session(invoice.invoice_id, "REASONING", reason_res)

            # Stage 9: Decision & Routing Agent
            logger.info(f"Stage 9: Running Decision Agent on invoice {invoice.invoice_id}")
            decision_res = decision_agent.run(db, invoice.id)
            memory_service.update_session(invoice.invoice_id, "DECISION", decision_res)

            # Record total processing time
            total_time_ms = int((time.time() - start_time) * 1000)
            invoice.processing_time_ms = total_time_ms
            db.commit()

            # Record completion audit log
            self._log_audit(
                db, "System Orchestrator", "AGENT", "PIPELINE_COMPLETE", "invoice", invoice.invoice_id,
                {"status": "processing"},
                {"final_decision": invoice.final_decision, "status": invoice.status, "risk_score": invoice.risk_score}
            )

            # Free short-term memory
            memory_service.clear_session(invoice.invoice_id)

            return {
                "invoice_id": invoice.invoice_id,
                "status": invoice.status,
                "final_decision": invoice.final_decision,
                "risk_score": invoice.risk_score,
                "risk_level": invoice.risk_level,
                "confidence": invoice.overall_confidence,
                "processing_time_ms": total_time_ms,
                "ai_recommendation": invoice.ai_recommendation,
                "reasons": invoice.decision_reasons
            }

        except Exception as e:
            logger.error(f"Orchestration failure on invoice {invoice.invoice_id}: {e}", exc_info=True)
            invoice.status = "review_required"
            invoice.final_decision = "REVIEW"
            invoice.decision_reasons = [f"Processing exception occurred: {str(e)}"]
            db.commit()
            
            self._log_audit(
                db, "System Orchestrator", "AGENT", "PIPELINE_ERROR", "invoice", invoice.invoice_id,
                None, {"error": str(e)}
            )
            return {
                "invoice_id": invoice.invoice_id,
                "status": "review_required",
                "final_decision": "REVIEW",
                "error": str(e)
            }

    def _log_audit(self, db: Session, actor: str, actor_type: str, action: str, entity: str, entity_id: str, before: Any, after: Any):
        log = AuditLog(
            actor_name=actor,
            actor_type=actor_type,
            action=action,
            entity=entity,
            entity_id=entity_id,
            before_state=before,
            after_state=after,
            result="SUCCESS"
        )
        db.add(log)
        db.commit()

orchestrator = InvoiceAgentOrchestrator()
