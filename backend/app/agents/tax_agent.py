import time
from typing import Any
from sqlalchemy.orm import Session
from backend.app.models.models import Invoice, InvoiceValidation, AgentRun, AgentToolCall
from backend.app.tools.agent_tools import validate_tax
from backend.app.core.config import settings

class TaxAgent:
    """
    Agent 4 — Tax Validation Agent
    Responsibilities:
    - Validate GST / CGST / SGST / IGST compliance
    - Compare expected tax vs invoice tax rate
    - Flag unauthorized tax rates with configurable tax master rules
    - Record execution run and tool calls
    """
    name = "Tax Validation Agent"

    def run(self, db: Session, invoice_id: int) -> dict[str, Any]:
        start_time = time.time()
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise ValueError(f"Invoice with ID {invoice_id} not found.")

        expected_rate = settings.DEFAULT_TAX_PERCENT
        
        # Invoke validate_tax tool
        tool_start = time.time()
        tax_result = validate_tax(
            subtotal=invoice.subtotal or 0.0,
            tax_amount=invoice.tax_amount or 0.0,
            tax_percentage=invoice.tax_percentage,
            expected_rate=expected_rate
        )
        tool_latency = int((time.time() - tool_start) * 1000)

        # Update validation record
        val_record = db.query(InvoiceValidation).filter(InvoiceValidation.invoice_id == invoice.id).first()
        if not val_record:
            val_record = InvoiceValidation(invoice_id=invoice.id)
            db.add(val_record)

        val_record.tax_status = tax_result["tax_status"]
        val_record.tax_type = tax_result["tax_type"]
        val_record.expected_tax_rate = tax_result["expected_tax_rate"]
        val_record.detected_tax_rate = tax_result["detected_tax_rate"]
        val_record.expected_tax_amount = tax_result["expected_tax_amount"]
        val_record.detected_tax_amount = tax_result["detected_tax_amount"]
        val_record.tax_difference = tax_result["tax_difference"]
        val_record.tax_notes = tax_result["tax_notes"]

        db.commit()

        execution_time_ms = int((time.time() - start_time) * 1000)

        # Record Agent Run & Tool Call
        agent_run = AgentRun(
            invoice_id=invoice.id,
            agent_name=self.name,
            status="COMPLETED" if tax_result["tax_status"] == "PASS" else "WARNING",
            execution_time_ms=execution_time_ms,
            input_data={"subtotal": invoice.subtotal, "tax_amount": invoice.tax_amount, "expected_rate": expected_rate},
            output_data=tax_result
        )
        db.add(agent_run)
        db.commit()
        db.refresh(agent_run)

        tool_call = AgentToolCall(
            agent_run_id=agent_run.id,
            tool_name="validate_tax",
            tool_arguments={
                "subtotal": invoice.subtotal,
                "tax_amount": invoice.tax_amount,
                "tax_percentage": invoice.tax_percentage,
                "expected_rate": expected_rate
            },
            tool_result=tax_result,
            execution_time_ms=tool_latency,
            status="SUCCESS"
        )
        db.add(tool_call)
        db.commit()

        return tax_result

tax_agent = TaxAgent()
