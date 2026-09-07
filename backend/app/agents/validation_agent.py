import time
from typing import Any
from sqlalchemy.orm import Session
from backend.app.models.models import Invoice, InvoiceValidation, AgentRun, AgentToolCall
from backend.app.tools.agent_tools import calculate_invoice_total

class ValidationAgent:
    """
    Agent 3 — Invoice Validation Agent
    Responsibilities:
    - Verify presence of mandatory fields
    - Verify line item mathematics (Quantity x Unit Price)
    - Perform holistic financial check: Subtotal - Discount + Tax == Total
    - Invoke calculate_invoice_total tool and record results
    """
    name = "Invoice Validation Agent"

    REQUIRED_FIELDS = [
        "invoice_number",
        "vendor_name_extracted",
        "invoice_date",
        "total_amount",
        "currency"
    ]

    def run(self, db: Session, invoice_id: int) -> dict[str, Any]:
        start_time = time.time()
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise ValueError(f"Invoice with ID {invoice_id} not found.")

        # 1. Required Fields Validation
        missing_fields = []
        for rf in self.REQUIRED_FIELDS:
            val = getattr(invoice, rf, None)
            if val is None or val == "" or val == 0.0:
                missing_fields.append(rf.replace("_extracted", ""))
        required_status = "PASS" if not missing_fields else "FAIL"

        # 2. Mathematical Validation via Tool
        tool_start = time.time()
        math_tool_result = calculate_invoice_total(
            subtotal=invoice.subtotal or 0.0,
            tax=invoice.tax_amount or 0.0,
            invoice_total=invoice.total_amount or 0.0,
            discount=invoice.discount or 0.0
        )
        tool_latency = int((time.time() - tool_start) * 1000)

        # 3. Line Items Math Check
        items_mismatch = []
        for item in invoice.items:
            expected_line_total = round((item.quantity * item.unit_price) - item.discount + item.tax_amount, 2)
            if abs(expected_line_total - item.total_price) > 1.0:
                items_mismatch.append(
                    f"Line '{item.description}': Expected ₹{expected_line_total:,.2f} vs Given ₹{item.total_price:,.2f}"
                )

        math_status = math_tool_result["status"]
        if items_mismatch:
            math_status = "MISMATCH"

        math_notes = math_tool_result["notes"]
        if items_mismatch:
            math_notes += " " + "; ".join(items_mismatch)

        # Create or update InvoiceValidation
        val_record = db.query(InvoiceValidation).filter(InvoiceValidation.invoice_id == invoice.id).first()
        if not val_record:
            val_record = InvoiceValidation(invoice_id=invoice.id)
            db.add(val_record)

        val_record.required_fields_status = required_status
        val_record.missing_fields = missing_fields
        val_record.math_status = math_status
        val_record.calculated_subtotal = invoice.subtotal
        val_record.calculated_total = math_tool_result["calculated_total"]
        val_record.invoice_total = invoice.total_amount
        val_record.math_difference = math_tool_result["difference"]
        val_record.math_notes = math_notes

        db.commit()

        execution_time_ms = int((time.time() - start_time) * 1000)

        output_data = {
            "required_fields_status": required_status,
            "missing_fields": missing_fields,
            "math_status": math_status,
            "calculated_total": math_tool_result["calculated_total"],
            "invoice_total": invoice.total_amount,
            "difference": math_tool_result["difference"],
            "math_notes": math_notes
        }

        # Record Agent Run & Tool Call
        agent_run = AgentRun(
            invoice_id=invoice.id,
            agent_name=self.name,
            status="COMPLETED" if math_status == "PASS" and required_status == "PASS" else "WARNING",
            execution_time_ms=execution_time_ms,
            input_data={"subtotal": invoice.subtotal, "tax": invoice.tax_amount, "total": invoice.total_amount},
            output_data=output_data
        )
        db.add(agent_run)
        db.commit()
        db.refresh(agent_run)

        tool_call = AgentToolCall(
            agent_run_id=agent_run.id,
            tool_name="calculate_invoice_total",
            tool_arguments={
                "subtotal": invoice.subtotal,
                "tax": invoice.tax_amount,
                "discount": invoice.discount,
                "invoice_total": invoice.total_amount
            },
            tool_result=math_tool_result,
            execution_time_ms=tool_latency,
            status="SUCCESS"
        )
        db.add(tool_call)
        db.commit()

        return output_data

validation_agent = ValidationAgent()
