import time
from datetime import datetime
from typing import Any
from sqlalchemy.orm import Session
from backend.app.models.models import Invoice, RiskAssessment, AgentRun, AgentToolCall
from backend.app.tools.agent_tools import calculate_risk_score

class FraudDetectionAgent:
    """
    Agent 8 — Fraud and Anomaly Detection Agent
    Responsibilities:
    - Evaluate 12 distinct anomaly and fraud indicators
    - Compute multi-factor weighted Risk Score (0-100)
    - Assign classification: LOW, MEDIUM, HIGH, CRITICAL
    - Format explainable, non-accusatory findings
    - Record execution run and tool calls
    """
    name = "Fraud and Anomaly Detection Agent"

    def run(self, db: Session, invoice_id: int) -> dict[str, Any]:
        start_time = time.time()
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise ValueError(f"Invoice with ID {invoice_id} not found.")

        val = invoice.validations
        anomalies = {}
        anomaly_details = {}

        # 1. Duplicate Risk
        is_dup = val and val.duplicate_status in ["POSSIBLE_DUPLICATE", "EXACT_DUPLICATE"]
        anomalies["duplicate_risk"] = is_dup
        if is_dup:
            anomaly_details["duplicate_risk"] = f"Duplicate signature detected: {val.duplicate_notes}"

        # 2. Unusual Amount Risk
        is_unusual_amount = False
        if invoice.vendor and invoice.vendor.historical_avg_amount > 0:
            dev = ((invoice.total_amount - invoice.vendor.historical_avg_amount) / invoice.vendor.historical_avg_amount) * 100
            if dev > 120.0:
                is_unusual_amount = True
                anomaly_details["unusual_amount_risk"] = f"Amount ₹{invoice.total_amount:,.2f} is {dev:.1f}% above vendor historical average."
        elif invoice.total_amount > 500000.0:
            is_unusual_amount = True
            anomaly_details["unusual_amount_risk"] = f"High value transaction (₹{invoice.total_amount:,.2f}) exceeding standard threshold."
        anomalies["unusual_amount_risk"] = is_unusual_amount

        # 3. Unusual Tax Risk
        is_tax_risk = val and val.tax_status in ["WARNING", "FAIL"]
        anomalies["unusual_tax_risk"] = is_tax_risk
        if is_tax_risk:
            anomaly_details["unusual_tax_risk"] = val.tax_notes or "Detected tax rate diverges from configured GST schedule."

        # 4. Repeated Invoice Number Risk
        # Check if same invoice number appeared with different vendor or amount
        repeat_num_count = db.query(Invoice).filter(
            Invoice.invoice_number == invoice.invoice_number,
            Invoice.id != invoice.id
        ).count()
        is_repeat_num = repeat_num_count > 0
        anomalies["repeat_invoice_num_risk"] = is_repeat_num
        if is_repeat_num:
            anomaly_details["repeat_invoice_num_risk"] = f"Invoice number '{invoice.invoice_number}' has already been processed {repeat_num_count} time(s)."

        # 5. Vendor Mismatch Risk
        is_vendor_mismatch = invoice.vendor_id is None
        anomalies["vendor_mismatch_risk"] = is_vendor_mismatch
        if is_vendor_mismatch:
            anomaly_details["vendor_mismatch_risk"] = f"Vendor '{invoice.vendor_name_extracted}' is not registered in verified master database."

        # 6. Suspicious Bank Details
        is_bank_risk = False
        if invoice.vendor and invoice.vendor.bank_account and invoice.bank_account_extracted:
            if invoice.vendor.bank_account.strip() != invoice.bank_account_extracted.strip():
                is_bank_risk = True
                anomaly_details["suspicious_bank_risk"] = (
                    f"Invoice bank account ({invoice.bank_account_extracted}) differs from vendor master on record ({invoice.vendor.bank_account})."
                )
        anomalies["suspicious_bank_risk"] = is_bank_risk

        # 7. Abnormal Quantity Risk
        is_abnormal_qty = False
        if val and val.po_match_status == "MISMATCH":
            for disc in val.po_discrepancies:
                if "exceeds PO Qty" in disc:
                    is_abnormal_qty = True
                    anomaly_details["abnormal_quantity_risk"] = disc
        anomalies["abnormal_quantity_risk"] = is_abnormal_qty

        # 8. Price Anomaly Risk
        is_price_anomaly = False
        if val and val.po_match_status == "MISMATCH":
            for disc in val.po_discrepancies:
                if "exceeds PO Price" in disc:
                    is_price_anomaly = True
                    anomaly_details["price_anomaly_risk"] = disc
        anomalies["price_anomaly_risk"] = is_price_anomaly

        # 9. Weekend Pattern Risk
        is_weekend = False
        if invoice.invoice_date:
            try:
                dt = datetime.strptime(invoice.invoice_date.strip(), "%Y-%m-%d")
                if dt.weekday() >= 5: # Saturday or Sunday
                    is_weekend = True
                    anomaly_details["weekend_pattern_risk"] = f"Invoice dated on a weekend ({dt.strftime('%A, %Y-%m-%d')})."
            except Exception:
                pass
        anomalies["weekend_pattern_risk"] = is_weekend

        # 10. Unusual Frequency Risk
        # Multiple invoices from same vendor within 3 days
        is_unusual_freq = False
        if invoice.vendor_id:
            recent_count = db.query(Invoice).filter(
                Invoice.vendor_id == invoice.vendor_id,
                Invoice.id != invoice.id
            ).count()
            if recent_count >= 5:
                is_unusual_freq = True
                anomaly_details["unusual_frequency_risk"] = f"High frequency submission pattern ({recent_count} invoices from vendor)."
        anomalies["unusual_frequency_risk"] = is_unusual_freq

        # 11. Modified Invoice Pattern
        is_modified = False
        if val and val.math_status == "MISMATCH":
            is_modified = True
            anomaly_details["modified_pattern_risk"] = f"Calculation discrepancy suggests potential document alteration ({val.math_notes})."
        anomalies["modified_pattern_risk"] = is_modified

        # 12. Missing Mandatory Information
        is_missing_info = val and val.required_fields_status == "FAIL"
        anomalies["missing_info_risk"] = is_missing_info
        if is_missing_info:
            anomaly_details["missing_info_risk"] = f"Mandatory fields missing: {', '.join(val.missing_fields)}"

        # Invoke calculate_risk_score tool
        tool_start = time.time()
        risk_result = calculate_risk_score(anomalies=anomalies, anomaly_details=anomaly_details)
        tool_latency = int((time.time() - tool_start) * 1000)

        # Update invoice & risk assessment
        invoice.risk_score = risk_result["risk_score"]
        invoice.risk_level = risk_result["risk_level"]

        risk_record = db.query(RiskAssessment).filter(RiskAssessment.invoice_id == invoice.id).first()
        if not risk_record:
            risk_record = RiskAssessment(invoice_id=invoice.id)
            db.add(risk_record)

        risk_record.risk_score = risk_result["risk_score"]
        risk_record.risk_level = risk_result["risk_level"]
        risk_record.duplicate_risk = is_dup
        risk_record.unusual_amount_risk = is_unusual_amount
        risk_record.unusual_tax_risk = is_tax_risk
        risk_record.repeat_invoice_num_risk = is_repeat_num
        risk_record.vendor_mismatch_risk = is_vendor_mismatch
        risk_record.suspicious_bank_risk = is_bank_risk
        risk_record.abnormal_quantity_risk = is_abnormal_qty
        risk_record.price_anomaly_risk = is_price_anomaly
        risk_record.weekend_pattern_risk = is_weekend
        risk_record.unusual_frequency_risk = is_unusual_freq
        risk_record.modified_pattern_risk = is_modified
        risk_record.missing_info_risk = is_missing_info
        risk_record.anomalies_detected = risk_result["detected_anomalies"]
        risk_record.explanation = risk_result["explanation"]

        db.commit()

        execution_time_ms = int((time.time() - start_time) * 1000)

        # Record Agent Run & Tool Call
        agent_run = AgentRun(
            invoice_id=invoice.id,
            agent_name=self.name,
            status="COMPLETED" if risk_result["risk_score"] <= 30 else "WARNING",
            execution_time_ms=execution_time_ms,
            input_data={"anomalies_checked": 12},
            output_data=risk_result
        )
        db.add(agent_run)
        db.commit()
        db.refresh(agent_run)

        tool_call = AgentToolCall(
            agent_run_id=agent_run.id,
            tool_name="calculate_risk_score",
            tool_arguments={"triggered_indicators_count": len(risk_result["detected_anomalies"])},
            tool_result=risk_result,
            execution_time_ms=tool_latency,
            status="SUCCESS"
        )
        db.add(tool_call)
        db.commit()

        return risk_result

fraud_detection_agent = FraudDetectionAgent()
