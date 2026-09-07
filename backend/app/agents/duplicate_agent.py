import time
from typing import Any
from sqlalchemy.orm import Session
from backend.app.models.models import Invoice, InvoiceValidation, AgentRun, AgentToolCall
from backend.app.tools.agent_tools import search_duplicate_invoice

class DuplicateAgent:
    """
    Agent 5 — Duplicate Detection Agent
    Responsibilities:
    - Search for exact duplicate binary hashes
    - Perform fuzzy similarity matching across invoice numbers and vendor names
    - Detect duplicate financial transactions
    - Record execution run and tool calls
    """
    name = "Duplicate Detection Agent"

    def run(self, db: Session, invoice_id: int) -> dict[str, Any]:
        start_time = time.time()
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise ValueError(f"Invoice with ID {invoice_id} not found.")

        # Invoke search_duplicate_invoice tool
        tool_start = time.time()
        dup_result = search_duplicate_invoice(
            db=db,
            invoice_number=invoice.invoice_number or "",
            vendor_name=invoice.vendor_name_extracted or "",
            amount=invoice.total_amount or 0.0,
            doc_hash=invoice.file_hash,
            exclude_id=invoice.id
        )
        tool_latency = int((time.time() - tool_start) * 1000)

        # Update validation record
        val_record = db.query(InvoiceValidation).filter(InvoiceValidation.invoice_id == invoice.id).first()
        if not val_record:
            val_record = InvoiceValidation(invoice_id=invoice.id)
            db.add(val_record)

        val_record.duplicate_status = dup_result["duplicate_status"]
        val_record.similarity_score = dup_result["similarity_score"]
        val_record.matched_invoice_id = dup_result.get("matched_invoice_id")
        val_record.duplicate_notes = dup_result["notes"]

        db.commit()

        execution_time_ms = int((time.time() - start_time) * 1000)

        # Record Agent Run & Tool Call
        agent_run = AgentRun(
            invoice_id=invoice.id,
            agent_name=self.name,
            status="COMPLETED" if dup_result["duplicate_status"] == "PASS" else "WARNING",
            execution_time_ms=execution_time_ms,
            input_data={
                "invoice_number": invoice.invoice_number,
                "vendor": invoice.vendor_name_extracted,
                "amount": invoice.total_amount
            },
            output_data=dup_result
        )
        db.add(agent_run)
        db.commit()
        db.refresh(agent_run)

        tool_call = AgentToolCall(
            agent_run_id=agent_run.id,
            tool_name="search_duplicate_invoice",
            tool_arguments={
                "invoice_number": invoice.invoice_number,
                "vendor_name": invoice.vendor_name_extracted,
                "amount": invoice.total_amount,
                "doc_hash": invoice.file_hash
            },
            tool_result=dup_result,
            execution_time_ms=tool_latency,
            status="SUCCESS"
        )
        db.add(tool_call)
        db.commit()

        return dup_result

duplicate_agent = DuplicateAgent()
