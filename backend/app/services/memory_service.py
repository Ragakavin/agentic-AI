import logging
from typing import Any, Optional
from sqlalchemy.orm import Session
from backend.app.models.models import HumanFeedback, Invoice, Vendor

logger = logging.getLogger("MemoryService")

class MemoryService:
    def __init__(self):
        # Short term in-memory session cache for active runs
        self._short_term_sessions: dict[str, dict[str, Any]] = {}

    def init_session(self, invoice_id: str, initial_data: dict[str, Any]):
        """Initialize short-term memory for an invoice processing lifecycle."""
        self._short_term_sessions[invoice_id] = {
            "invoice_id": invoice_id,
            "stage_history": [],
            "current_stage": "INTAKE",
            "context": initial_data
        }

    def update_session(self, invoice_id: str, stage: str, stage_data: dict[str, Any]):
        """Store intermediate agent outputs in short term memory."""
        if invoice_id not in self._short_term_sessions:
            self.init_session(invoice_id, {})
        
        session = self._short_term_sessions[invoice_id]
        session["current_stage"] = stage
        session["stage_history"].append(stage)
        session["context"][stage.lower()] = stage_data

    def get_session_context(self, invoice_id: str) -> dict[str, Any]:
        """Retrieve full active short-term memory context."""
        return self._short_term_sessions.get(invoice_id, {}).get("context", {})

    def clear_session(self, invoice_id: str):
        """Free short-term memory once invoice processing completes."""
        if invoice_id in self._short_term_sessions:
            del self._short_term_sessions[invoice_id]

    def record_human_override(
        self,
        db: Session,
        invoice_id: int,
        vendor_id: Optional[int],
        original_ai_decision: str,
        human_decision: str,
        reason: str,
        context: dict[str, Any]
    ) -> HumanFeedback:
        """Persist human reviewer overrides to long-term memory."""
        feedback = HumanFeedback(
            invoice_id=invoice_id,
            vendor_id=vendor_id,
            original_ai_decision=original_ai_decision,
            human_decision=human_decision,
            reason_given=reason,
            feedback_context=context
        )
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        logger.info(f"Recorded human feedback into long-term memory for invoice {invoice_id}")
        return feedback

    def get_vendor_historical_context(self, db: Session, vendor_id: Optional[int], vendor_name: Optional[str]) -> dict[str, Any]:
        """Retrieve long-term memory patterns for vendor behavior and past overrides."""
        if not vendor_id and not vendor_name:
            return {"past_overrides_count": 0, "patterns": []}

        query = db.query(HumanFeedback)
        if vendor_id:
            query = query.filter(HumanFeedback.vendor_id == vendor_id)
        
        feedbacks = query.order_by(HumanFeedback.created_at.desc()).limit(5).all()
        
        patterns = []
        for fb in feedbacks:
            patterns.append({
                "original_ai": fb.original_ai_decision,
                "human_override": fb.human_decision,
                "reason": fb.reason_given,
                "date": fb.created_at.strftime("%Y-%m-%d")
            })

        return {
            "past_overrides_count": len(feedbacks),
            "patterns": patterns
        }

memory_service = MemoryService()
