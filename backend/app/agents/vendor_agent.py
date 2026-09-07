import time
from typing import Any
from sqlalchemy.orm import Session
from backend.app.models.models import Invoice, Vendor, AgentRun, AgentToolCall
from backend.app.tools.agent_tools import get_vendor

class VendorVerificationAgent:
    """
    Agent 7 — Vendor Verification Agent
    Responsibilities:
    - Match invoice against approved Vendor master database
    - Verify vendor Tax ID (GSTIN)
    - Calculate historical spend deviations
    - Assess vendor behavioral risk
    - Record execution run and tool calls
    """
    name = "Vendor Verification Agent"

    def run(self, db: Session, invoice_id: int) -> dict[str, Any]:
        start_time = time.time()
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise ValueError(f"Invoice with ID {invoice_id} not found.")

        vendor_name = invoice.vendor_name_extracted
        
        tool_start = time.time()
        vendor_data = get_vendor(db=db, vendor_name=vendor_name)
        tool_latency = int((time.time() - tool_start) * 1000)

        deviation_pct = 0.0
        historical_avg = 0.0
        vendor_risk = "LOW"
        notes = []

        if vendor_data:
            invoice.vendor_id = vendor_data["id"]
            db.commit()

            historical_avg = vendor_data.get("historical_avg_amount", 0.0)
            vendor_risk = vendor_data.get("risk_level", "LOW")
            
            # Check Tax ID consistency
            extracted_tax_id = invoice.vendor_tax_id_extracted
            master_tax_id = vendor_data.get("tax_id")
            if master_tax_id and extracted_tax_id:
                if master_tax_id.strip().upper() != extracted_tax_id.strip().upper():
                    notes.append(f"Tax ID mismatch: Master '{master_tax_id}' vs Extracted '{extracted_tax_id}'.")

            # Check historical spending deviation
            if historical_avg > 0 and invoice.total_amount:
                deviation_pct = round(((invoice.total_amount - historical_avg) / historical_avg) * 100.0, 1)
                if deviation_pct > 100.0:
                    notes.append(
                        f"Current amount ₹{invoice.total_amount:,.2f} deviates by +{deviation_pct}% from historical avg (₹{historical_avg:,.2f})."
                    )
        else:
            vendor_risk = "MEDIUM"
            notes.append(f"Vendor '{vendor_name}' is not registered in system master.")

        execution_time_ms = int((time.time() - start_time) * 1000)

        output_data = {
            "vendor_matched": bool(vendor_data),
            "vendor_id": vendor_data["id"] if vendor_data else None,
            "vendor_name": vendor_data["name"] if vendor_data else vendor_name,
            "vendor_risk": vendor_risk,
            "historical_average": historical_avg,
            "current_amount": invoice.total_amount or 0.0,
            "deviation_percentage": deviation_pct,
            "notes": "; ".join(notes) if notes else "Vendor verified with approved master."
        }

        # Record Agent Run & Tool Call
        agent_run = AgentRun(
            invoice_id=invoice.id,
            agent_name=self.name,
            status="COMPLETED" if not notes else "WARNING",
            execution_time_ms=execution_time_ms,
            input_data={"vendor_name": vendor_name, "invoice_amount": invoice.total_amount},
            output_data=output_data
        )
        db.add(agent_run)
        db.commit()
        db.refresh(agent_run)

        tool_call = AgentToolCall(
            agent_run_id=agent_run.id,
            tool_name="get_vendor",
            tool_arguments={"vendor_name": vendor_name},
            tool_result=output_data,
            execution_time_ms=tool_latency,
            status="SUCCESS"
        )
        db.add(tool_call)
        db.commit()

        return output_data

vendor_verification_agent = VendorVerificationAgent()
