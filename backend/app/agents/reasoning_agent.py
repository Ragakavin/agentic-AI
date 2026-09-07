import time
from typing import Any
from sqlalchemy.orm import Session
from backend.app.models.models import Invoice, AgentRun, AgentToolCall
from backend.app.services.llm_service import llm_service
from backend.app.services.memory_service import memory_service

class ReasoningAgent:
    """
    Agent 9 — AI Reasoning Agent
    Responsibilities:
    - Synthesize verified evidence from all specialized agents
    - Incorporate long-term memory patterns (vendor historical overrides)
    - Invoke LLM reasoning layer to construct explainable rationale
    - Strictly ground decisions on verified evidence
    - Record execution run and tool calls
    """
    name = "AI Reasoning Agent"

    async def run(self, db: Session, invoice_id: int) -> dict[str, Any]:
        start_time = time.time()
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise ValueError(f"Invoice with ID {invoice_id} not found.")

        val = invoice.validations
        risk = invoice.risk_assessment

        # Retrieve long-term vendor history context
        vendor_history = memory_service.get_vendor_historical_context(
            db=db,
            vendor_id=invoice.vendor_id,
            vendor_name=invoice.vendor_name_extracted
        )

        # Assemble comprehensive evidence packet
        evidence_packet = {
            "invoice_metadata": {
                "invoice_id": invoice.invoice_id,
                "invoice_number": invoice.invoice_number,
                "vendor": invoice.vendor_name_extracted,
                "total_amount": invoice.total_amount,
                "currency": invoice.currency,
                "extraction_confidence": invoice.overall_confidence
            },
            "validation": {
                "required_fields_status": val.required_fields_status if val else "PASS",
                "missing_fields": val.missing_fields if val else [],
                "math_status": val.math_status if val else "PASS",
                "math_difference": val.math_difference if val else 0.0,
                "math_notes": val.math_notes if val else ""
            },
            "tax": {
                "tax_status": val.tax_status if val else "PASS",
                "expected_tax_rate": val.expected_tax_rate if val else 18.0,
                "detected_tax_rate": val.detected_tax_rate if val else 18.0,
                "tax_difference": val.tax_difference if val else 0.0,
                "tax_notes": val.tax_notes if val else ""
            },
            "duplicate": {
                "duplicate_status": val.duplicate_status if val else "PASS",
                "similarity_score": val.similarity_score if val else 0.0,
                "matched_invoice_id": val.matched_invoice_id if val else None,
                "duplicate_notes": val.duplicate_notes if val else ""
            },
            "po_matching": {
                "po_match_status": val.po_match_status if val else "PASS",
                "po_number": val.po_number if val else None,
                "po_discrepancies": val.po_discrepancies if val else []
            },
            "fraud": {
                "risk_score": risk.risk_score if risk else 0.0,
                "risk_level": risk.risk_level if risk else "LOW",
                "anomalies": risk.anomalies_detected if risk else []
            },
            "vendor": {
                "vendor_name": invoice.vendor.name if invoice.vendor else invoice.vendor_name_extracted,
                "historical_avg": invoice.vendor.historical_avg_amount if invoice.vendor else 0.0,
                "deviation_percentage": round(((invoice.total_amount - invoice.vendor.historical_avg_amount) / invoice.vendor.historical_avg_amount)*100, 1) if (invoice.vendor and invoice.vendor.historical_avg_amount > 0) else 0.0
            },
            "long_term_memory": vendor_history
        }

        # Invoke LLM Service
        tool_start = time.time()
        reasoning_result = await llm_service.generate_reasoning(evidence_packet)
        tool_latency = int((time.time() - tool_start) * 1000)

        # Update Invoice with synthesis
        invoice.ai_recommendation = reasoning_result.get("decision", "REVIEW")
        invoice.decision_reasons = reasoning_result.get("reasons", [])
        invoice.recommended_action = reasoning_result.get("recommended_action", "Review invoice.")
        invoice.reasoning_summary = " | ".join(reasoning_result.get("reasons", []))
        db.commit()

        execution_time_ms = int((time.time() - start_time) * 1000)

        # Record Agent Run & Tool Call
        agent_run = AgentRun(
            invoice_id=invoice.id,
            agent_name=self.name,
            status="COMPLETED",
            execution_time_ms=execution_time_ms,
            input_data={"evidence_keys": list(evidence_packet.keys())},
            output_data=reasoning_result
        )
        db.add(agent_run)
        db.commit()
        db.refresh(agent_run)

        tool_call = AgentToolCall(
            agent_run_id=agent_run.id,
            tool_name="generate_reasoning",
            tool_arguments={"llm_provider": llm_service.provider, "evidence_summary": invoice.ai_recommendation},
            tool_result=reasoning_result,
            execution_time_ms=tool_latency,
            status="SUCCESS"
        )
        db.add(tool_call)
        db.commit()

        return reasoning_result

reasoning_agent = ReasoningAgent()
