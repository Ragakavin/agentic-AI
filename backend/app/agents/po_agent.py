import time
from typing import Any
from sqlalchemy.orm import Session
from backend.app.models.models import Invoice, InvoiceValidation, AgentRun, AgentToolCall, PurchaseOrder
from backend.app.tools.agent_tools import get_purchase_order, compare_invoice_with_po
from backend.app.core.config import settings

class POMatchingAgent:
    """
    Agent 6 — Purchase Order Matching Agent
    Responsibilities:
    - Retrieve referenced Purchase Order from system database
    - Perform 3-way line item match (quantity, unit price, totals)
    - Apply configurable tolerances (5% qty, 3% unit price)
    - Record execution run and tool calls
    """
    name = "Purchase Order Matching Agent"

    def run(self, db: Session, invoice_id: int) -> dict[str, Any]:
        start_time = time.time()
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise ValueError(f"Invoice with ID {invoice_id} not found.")

        # Find PO reference from extracted fields
        po_extracted = (invoice.extracted_fields or {}).get("po_number", {}).get("value")
        if not po_extracted and invoice.purchase_order:
            po_extracted = invoice.purchase_order.po_number

        tool_start = time.time()
        po_record = None
        if po_extracted:
            po_record = get_purchase_order(db=db, po_number=po_extracted)
        po_fetch_latency = int((time.time() - tool_start) * 1000)

        # Prepare line items format
        inv_items = [
            {
                "description": it.description,
                "quantity": it.quantity,
                "unit_price": it.unit_price,
                "tax_rate": it.tax_rate,
                "total_price": it.total_price
            }
            for it in invoice.items
        ]

        if not po_record:
            po_match_status = "NOT_FOUND"
            discrepancies = [f"No Purchase Order found for reference '{po_extracted or 'N/A'}'."]
            compare_result = {
                "po_match_status": po_match_status,
                "po_discrepancies": discrepancies,
                "matched_items_count": 0
            }
            compare_latency = 0
        else:
            invoice.po_id = po_record["id"]
            db.commit()

            tool_compare_start = time.time()
            compare_result = compare_invoice_with_po(
                invoice_items=inv_items,
                po_items=po_record["items"],
                invoice_total=invoice.total_amount or 0.0,
                po_total=po_record["total_amount"],
                qty_tolerance_pct=settings.PO_QUANTITY_TOLERANCE_PCT,
                price_tolerance_pct=settings.PO_PRICE_TOLERANCE_PCT
            )
            compare_latency = int((time.time() - tool_compare_start) * 1000)

        # Update validation record
        val_record = db.query(InvoiceValidation).filter(InvoiceValidation.invoice_id == invoice.id).first()
        if not val_record:
            val_record = InvoiceValidation(invoice_id=invoice.id)
            db.add(val_record)

        val_record.po_match_status = compare_result["po_match_status"]
        val_record.po_number = po_extracted
        val_record.po_discrepancies = compare_result.get("po_discrepancies", [])
        db.commit()

        execution_time_ms = int((time.time() - start_time) * 1000)

        # Record Agent Run & Tool Call
        agent_run = AgentRun(
            invoice_id=invoice.id,
            agent_name=self.name,
            status="COMPLETED" if compare_result["po_match_status"] == "PASS" else "WARNING",
            execution_time_ms=execution_time_ms,
            input_data={"po_number": po_extracted, "line_items_count": len(inv_items)},
            output_data=compare_result
        )
        db.add(agent_run)
        db.commit()
        db.refresh(agent_run)

        tool_call = AgentToolCall(
            agent_run_id=agent_run.id,
            tool_name="compare_invoice_with_po",
            tool_arguments={
                "po_number": po_extracted,
                "qty_tolerance_pct": settings.PO_QUANTITY_TOLERANCE_PCT,
                "price_tolerance_pct": settings.PO_PRICE_TOLERANCE_PCT
            },
            tool_result=compare_result,
            execution_time_ms=po_fetch_latency + compare_latency,
            status="SUCCESS"
        )
        db.add(tool_call)
        db.commit()

        return compare_result

po_matching_agent = POMatchingAgent()
