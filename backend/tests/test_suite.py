import pytest
from backend.app.tools.agent_tools import (
    calculate_invoice_total,
    validate_tax,
    compare_invoice_with_po,
    calculate_risk_score
)
from backend.app.core.config import settings

def test_mathematical_validation_pass():
    res = calculate_invoice_total(subtotal=50000.0, tax=9000.0, invoice_total=59000.0, discount=0.0)
    assert res["status"] == "PASS"
    assert res["difference"] == 0.0

def test_mathematical_validation_mismatch():
    res = calculate_invoice_total(subtotal=50000.0, tax=9000.0, invoice_total=61000.0, discount=0.0)
    assert res["status"] == "MISMATCH"
    assert res["difference"] == 2000.0

def test_tax_validation_clean():
    res = validate_tax(subtotal=50000.0, tax_amount=9000.0, tax_percentage=18.0, expected_rate=18.0)
    assert res["tax_status"] == "PASS"
    assert res["tax_difference"] == 0.0

def test_tax_validation_deviation():
    # 28% GST detected instead of expected 18%
    res = validate_tax(subtotal=80000.0, tax_amount=22400.0, tax_percentage=28.0, expected_rate=18.0)
    assert res["tax_status"] == "FAIL"
    assert res["detected_tax_rate"] == 28.0
    assert res["tax_difference"] == 8000.0

def test_po_matching_exact():
    inv_items = [{"description": "Cloud Hosting", "quantity": 10.0, "unit_price": 5000.0}]
    po_items = [{"description": "Cloud Hosting", "quantity": 10.0, "unit_price": 5000.0}]
    res = compare_invoice_with_po(inv_items, po_items, invoice_total=59000.0, po_total=59000.0)
    assert res["po_match_status"] == "PASS"
    assert len(res["po_discrepancies"]) == 0

def test_po_matching_quantity_mismatch():
    # Quantity 120 on invoice vs 100 on PO (+20% diff, tolerance is 5%)
    inv_items = [{"description": "Software User Licenses", "quantity": 120.0, "unit_price": 882.77}]
    po_items = [{"description": "Software User Licenses", "quantity": 100.0, "unit_price": 882.77}]
    res = compare_invoice_with_po(
        inv_items, po_items, invoice_total=125000.0, po_total=104166.86,
        qty_tolerance_pct=5.0, price_tolerance_pct=3.0
    )
    assert res["po_match_status"] == "MISMATCH"
    assert any("exceeds PO Qty" in d for d in res["po_discrepancies"])

def test_fraud_risk_scoring():
    anomalies = {
        "duplicate_risk": True,
        "repeat_invoice_num_risk": True,
        "unusual_amount_risk": False
    }
    res = calculate_risk_score(anomalies)
    assert res["risk_score"] >= 70.0
    assert res["risk_level"] in ["HIGH", "CRITICAL"]
    assert "Potential risk detected" in res["explanation"]

def test_clean_risk_scoring():
    anomalies = {
        "duplicate_risk": False,
        "unusual_amount_risk": False,
        "unusual_tax_risk": False
    }
    res = calculate_risk_score(anomalies)
    assert res["risk_score"] == 0.0
    assert res["risk_level"] == "LOW"
