from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session
from backend.app.models.models import (
    Role, User, Vendor, PurchaseOrder, PurchaseOrderItem, Invoice, InvoiceItem,
    InvoiceValidation, RiskAssessment, ReviewTask, Notification, AuditLog, SystemSetting
)
from backend.app.api.auth import hash_password
from backend.app.core.config import settings

def seed_database(db: Session):
    """Seed initial roles, demo users, vendors, POs, and benchmark invoices."""
    
    # 1. Roles
    role_names = [
        ("admin", "Full administrative access and settings configuration"),
        ("finance_manager", "Financial review, approval rights, and reporting"),
        ("reviewer", "Assigned human-in-the-loop review tasks"),
        ("viewer", "Read-only access to invoices and dashboard analytics")
    ]
    roles_map = {}
    for r_name, r_desc in role_names:
        role = db.query(Role).filter(Role.name == r_name).first()
        if not role:
            role = Role(name=r_name, description=r_desc)
            db.add(role)
            db.commit()
            db.refresh(role)
        roles_map[r_name] = role

    # 2. Demo Users
    demo_users = [
        ("admin@enterprise.ai", "Sarah Connor (Admin)", "admin", "admin123"),
        ("finance@enterprise.ai", "Alexander Hamilton (Finance Manager)", "finance_manager", "finance123"),
        ("reviewer@enterprise.ai", "Eleanor Vance (Reviewer)", "reviewer", "reviewer123"),
        ("viewer@enterprise.ai", "Arthur Dent (Viewer)", "viewer", "viewer123")
    ]
    for email, name, r_name, pwd in demo_users:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                email=email,
                name=name,
                hashed_password=hash_password(pwd),
                role_id=roles_map[r_name].id,
                is_active=True
            )
            db.add(user)
    db.commit()

    # 3. Vendors
    vendors_data = [
        {
            "vendor_code": "VEND-001",
            "name": "ABC Technologies Pvt Ltd",
            "tax_id": "29AABCA1234F1Z8",
            "email": "billing@abctechnologies.com",
            "phone": "+91 80 4123 4567",
            "address": "402 Tech Park, Outer Ring Road, Bangalore - 560103",
            "risk_level": "LOW",
            "historical_avg_amount": 55000.0,
            "total_invoices_count": 24,
            "bank_account": "987654321001",
            "bank_name": "HDFC Bank"
        },
        {
            "vendor_code": "VEND-002",
            "name": "XYZ Solutions Corp",
            "tax_id": "29XYZAB9876K1Z2",
            "email": "accounts@xyzsolutions.com",
            "phone": "+91 80 8899 0011",
            "address": "78 Business Tower, Whitefield, Bangalore",
            "risk_level": "MEDIUM",
            "historical_avg_amount": 45000.0,
            "total_invoices_count": 12,
            "bank_account": "554433221100",
            "bank_name": "ICICI Bank"
        },
        {
            "vendor_code": "VEND-003",
            "name": "Delta Hardware & Systems",
            "tax_id": "07DELAB5544P1Z3",
            "email": "finance@deltasystems.in",
            "phone": "+91 124 556 7788",
            "address": "12 Industrial Area, Sector 5, Gurgaon",
            "risk_level": "HIGH",
            "historical_avg_amount": 75000.0,
            "total_invoices_count": 8,
            "bank_account": "112233445566",
            "bank_name": "State Bank of India"
        }
    ]
    vendors_map = {}
    for v_info in vendors_data:
        v = db.query(Vendor).filter(Vendor.vendor_code == v_info["vendor_code"]).first()
        if not v:
            v = Vendor(**v_info)
            db.add(v)
            db.commit()
            db.refresh(v)
        vendors_map[v.name] = v

    # 4. Purchase Orders
    po_data = [
        {
            "po_number": "PO-2026-001",
            "vendor_id": vendors_map["ABC Technologies Pvt Ltd"].id,
            "currency": "INR",
            "subtotal": 50000.0,
            "tax_amount": 9000.0,
            "total_amount": 59000.0,
            "status": "OPEN",
            "items": [
                {
                    "item_description": "Cloud Hosting & Managed Services",
                    "quantity": 10.0,
                    "unit_price": 5000.0,
                    "tax_rate": 18.0,
                    "total_price": 59000.0
                }
            ]
        },
        {
            "po_number": "PO-2026-042",
            "vendor_id": vendors_map["XYZ Solutions Corp"].id,
            "currency": "INR",
            "subtotal": 88277.0,
            "tax_amount": 15889.86,
            "total_amount": 104166.86,
            "status": "OPEN",
            "items": [
                {
                    "item_description": "Enterprise Software User Licenses",
                    "quantity": 100.0,  # Note: Invoice 2 requests 120 (mismatch!)
                    "unit_price": 882.77,
                    "tax_rate": 18.0,
                    "total_price": 104166.86
                }
            ]
        },
        {
            "po_number": "PO-2026-088",
            "vendor_id": vendors_map["Delta Hardware & Systems"].id,
            "currency": "INR",
            "subtotal": 80000.0,
            "tax_amount": 14400.0,
            "total_amount": 94400.0,
            "status": "OPEN",
            "items": [
                {
                    "item_description": "Server Hardware Components",
                    "quantity": 4.0,
                    "unit_price": 20000.0,
                    "tax_rate": 18.0,
                    "total_price": 94400.0
                }
            ]
        }
    ]
    po_map = {}
    for p_info in po_data:
        po = db.query(PurchaseOrder).filter(PurchaseOrder.po_number == p_info["po_number"]).first()
        if not po:
            items_list = p_info.pop("items")
            po = PurchaseOrder(**p_info)
            db.add(po)
            db.commit()
            db.refresh(po)
            for it in items_list:
                po_it = PurchaseOrderItem(po_id=po.id, **it)
                db.add(po_it)
            db.commit()
        po_map[po.po_number] = po

    # Create dummy sample invoice files in uploads dir
    sample_files = [
        ("invoice_1_clean.pdf", "Invoice 1 Clean - ABC Technologies"),
        ("invoice_2_po_mismatch.pdf", "Invoice 2 PO Mismatch - XYZ Solutions"),
        ("invoice_3_duplicate.pdf", "Invoice 3 Duplicate - ABC Technology"),
        ("invoice_4_tax_mismatch.pdf", "Invoice 4 Tax Discrepancy - Delta Systems")
    ]
    for fn, content in sample_files:
        fp = settings.UPLOAD_DIR / fn
        if not fp.exists():
            with open(fp, "w", encoding="utf-8") as f:
                f.write(f"%PDF-1.4\n% Sample Agentic AI Test Invoice: {content}\n")

    # 5. Benchmark Invoice Records (if not already existing)
    if db.query(Invoice).count() == 0:
        # Benchmark 1: Clean Invoice
        inv1 = Invoice(
            invoice_id="INV-SYS-001",
            invoice_number="INV-10025",
            original_filename="invoice_1_clean.pdf",
            file_type="PDF",
            file_path=str(settings.UPLOAD_DIR / "invoice_1_clean.pdf"),
            file_size_bytes=142500,
            file_hash="7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069",
            vendor_id=vendors_map["ABC Technologies Pvt Ltd"].id,
            po_id=po_map["PO-2026-001"].id,
            vendor_name_extracted="ABC Technologies Pvt Ltd",
            vendor_address_extracted="402 Tech Park, Outer Ring Road, Bangalore - 560103",
            vendor_email_extracted="billing@abctechnologies.com",
            vendor_tax_id_extracted="29AABCA1234F1Z8",
            invoice_date="2026-09-01",
            due_date="2026-09-30",
            currency="INR",
            payment_terms="Net 30",
            subtotal=50000.0,
            discount=0.0,
            tax_amount=9000.0,
            tax_percentage=18.0,
            total_amount=59000.0,
            bank_account_extracted="987654321001",
            bank_ifsc_extracted="HDFC0001234",
            status="approved",
            final_decision="APPROVE",
            overall_confidence=0.98,
            risk_score=15.0,
            risk_level="LOW",
            ai_recommendation="APPROVE",
            reasoning_summary="All automated validations, tax compliance, and PO matching checks passed with high confidence.",
            decision_reasons=["Passed mathematical verification", "PO reference matched exactly", "No duplicate signatures"],
            recommended_action="Automatic approval recommended for payment processing.",
            processing_time_ms=1240
        )
        db.add(inv1)
        db.commit()
        db.refresh(inv1)

        db.add(InvoiceItem(
            invoice_id=inv1.id, description="Cloud Hosting & Managed Services",
            quantity=10.0, unit_price=5000.0, discount=0.0, tax_rate=18.0, tax_amount=9000.0,
            total_price=59000.0, confidence=0.98
        ))
        db.add(InvoiceValidation(
            invoice_id=inv1.id, required_fields_status="PASS", math_status="PASS",
            calculated_subtotal=50000.0, calculated_total=59000.0, invoice_total=59000.0,
            math_difference=0.0, math_notes="Calculations match.", tax_status="PASS",
            tax_type="GST (CGST/SGST/IGST)", expected_tax_rate=18.0, detected_tax_rate=18.0,
            expected_tax_amount=9000.0, detected_tax_amount=9000.0, tax_difference=0.0,
            tax_notes="Tax rate complies with 18% rule.", po_match_status="PASS",
            po_number="PO-2026-001", po_discrepancies=[], duplicate_status="PASS",
            similarity_score=0.10, duplicate_notes="No duplicate invoices detected in system database."
        ))
        db.add(RiskAssessment(
            invoice_id=inv1.id, risk_score=15.0, risk_level="LOW",
            anomalies_detected=[], explanation="Low risk profile — all parameters within standard bounds."
        ))

        # Benchmark 2: PO Mismatch Invoice
        inv2 = Invoice(
            invoice_id="INV-SYS-002",
            invoice_number="INV-20450",
            original_filename="invoice_2_po_mismatch.pdf",
            file_type="PDF",
            file_path=str(settings.UPLOAD_DIR / "invoice_2_po_mismatch.pdf"),
            file_size_bytes=188000,
            file_hash="a1b2c3d4e5f6789012345678abcdef1234567890abcdef1234567890abcdef12",
            vendor_id=vendors_map["XYZ Solutions Corp"].id,
            po_id=po_map["PO-2026-042"].id,
            vendor_name_extracted="XYZ Solutions Corp",
            vendor_address_extracted="78 Business Tower, Whitefield, Bangalore",
            vendor_email_extracted="accounts@xyzsolutions.com",
            vendor_tax_id_extracted="29XYZAB9876K1Z2",
            invoice_date="2026-09-02",
            due_date="2026-10-02",
            currency="INR",
            payment_terms="Net 30",
            subtotal=105932.20,
            discount=0.0,
            tax_amount=19067.80,
            tax_percentage=18.0,
            total_amount=125000.0,
            bank_account_extracted="554433221100",
            bank_ifsc_extracted="ICIC0005678",
            status="review_required",
            final_decision="REVIEW",
            overall_confidence=0.94,
            risk_score=75.0,
            risk_level="HIGH",
            ai_recommendation="REVIEW",
            reasoning_summary="Purchase order quantity mismatch | Vendor amount deviation (+177%)",
            decision_reasons=[
                "Line 'Enterprise Software User Licenses': Invoice Qty 120 exceeds PO Qty 100 by +20 (20.0% diff, tolerance is 5.0%)",
                "Vendor invoice amount ₹125,000.00 deviates by +177.8% from historical avg (₹45,000.00)"
            ],
            recommended_action="Routing to Accounts Payable Human-in-the-Loop review queue for verification.",
            processing_time_ms=1450
        )
        db.add(inv2)
        db.commit()
        db.refresh(inv2)

        db.add(InvoiceItem(
            invoice_id=inv2.id, description="Enterprise Software User Licenses",
            quantity=120.0, unit_price=882.77, discount=0.0, tax_rate=18.0, tax_amount=19067.80,
            total_price=125000.0, confidence=0.97
        ))
        db.add(InvoiceValidation(
            invoice_id=inv2.id, required_fields_status="PASS", math_status="PASS",
            calculated_subtotal=105932.20, calculated_total=125000.0, invoice_total=125000.0,
            math_difference=0.0, math_notes="Calculations match.", tax_status="PASS",
            tax_type="GST (CGST/SGST/IGST)", expected_tax_rate=18.0, detected_tax_rate=18.0,
            expected_tax_amount=19067.80, detected_tax_amount=19067.80, tax_difference=0.0,
            tax_notes="Tax rate complies with 18% rule.", po_match_status="MISMATCH",
            po_number="PO-2026-042", po_discrepancies=["Invoice Qty 120 exceeds PO Qty 100 by +20 (20% diff, tolerance 5%)"],
            duplicate_status="PASS", similarity_score=0.15, duplicate_notes="No duplicate detected."
        ))
        db.add(RiskAssessment(
            invoice_id=inv2.id, risk_score=75.0, risk_level="HIGH",
            abnormal_quantity_risk=True, unusual_amount_risk=True,
            anomalies_detected=[
                {"indicator": "abnormal_quantity_risk", "weight": 20.0, "detail": "Quantity exceeds PO by 20 units"},
                {"indicator": "unusual_amount_risk", "weight": 20.0, "detail": "Amount deviates by +177% from historical average"}
            ],
            explanation="Potential risk detected — human review recommended."
        ))
        db.add(ReviewTask(
            invoice_id=inv2.id, status="PENDING", original_ai_decision="REVIEW",
            ai_risk_score=75.0, reason="Purchase order quantity mismatch (+20 units)"
        ))

        # Benchmark 3: Duplicate Invoice
        inv3 = Invoice(
            invoice_id="INV-SYS-003",
            invoice_number="INV-10025",
            original_filename="invoice_3_duplicate.pdf",
            file_type="PDF",
            file_path=str(settings.UPLOAD_DIR / "invoice_3_duplicate.pdf"),
            file_size_bytes=142800,
            file_hash="999991657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9999",
            vendor_id=vendors_map["ABC Technologies Pvt Ltd"].id,
            po_id=po_map["PO-2026-001"].id,
            vendor_name_extracted="ABC Technology Pvt Ltd",
            vendor_address_extracted="402 Tech Park, Outer Ring Road, Bangalore - 560103",
            vendor_email_extracted="billing@abctechnologies.com",
            vendor_tax_id_extracted="29AABCA1234F1Z8",
            invoice_date="2026-09-01",
            due_date="2026-09-30",
            currency="INR",
            payment_terms="Net 30",
            subtotal=50000.0,
            discount=0.0,
            tax_amount=9000.0,
            tax_percentage=18.0,
            total_amount=59000.0,
            bank_account_extracted="987654321001",
            bank_ifsc_extracted="HDFC0001234",
            status="review_required",
            final_decision="REVIEW",
            overall_confidence=0.96,
            risk_score=85.0,
            risk_level="CRITICAL",
            ai_recommendation="REVIEW",
            reasoning_summary="Potential duplicate invoice detected with 94.0% similarity to existing records",
            decision_reasons=[
                "High similarity (94.0%) detected with prior invoice INV-SYS-001 (INV-10025)",
                "Invoice number 'INV-10025' has already been processed previously"
            ],
            recommended_action="Reject invoice or verify with vendor to avoid double payment.",
            processing_time_ms=1320
        )
        db.add(inv3)
        db.commit()
        db.refresh(inv3)

        db.add(InvoiceItem(
            invoice_id=inv3.id, description="Cloud Hosting & Managed Services",
            quantity=10.0, unit_price=5000.0, discount=0.0, tax_rate=18.0, tax_amount=9000.0,
            total_price=59000.0, confidence=0.98
        ))
        db.add(InvoiceValidation(
            invoice_id=inv3.id, required_fields_status="PASS", math_status="PASS",
            calculated_subtotal=50000.0, calculated_total=59000.0, invoice_total=59000.0,
            math_difference=0.0, math_notes="Calculations match.", tax_status="PASS",
            tax_type="GST (CGST/SGST/IGST)", expected_tax_rate=18.0, detected_tax_rate=18.0,
            expected_tax_amount=9000.0, detected_tax_amount=9000.0, tax_difference=0.0,
            tax_notes="Tax rate complies with 18% rule.", po_match_status="PASS",
            po_number="PO-2026-001", po_discrepancies=[], duplicate_status="POSSIBLE_DUPLICATE",
            similarity_score=0.94, matched_invoice_id="INV-SYS-001",
            duplicate_notes="High similarity (94.0%) detected with prior invoice INV-SYS-001."
        ))
        db.add(RiskAssessment(
            invoice_id=inv3.id, risk_score=85.0, risk_level="CRITICAL",
            duplicate_risk=True, repeat_invoice_num_risk=True,
            anomalies_detected=[
                {"indicator": "duplicate_risk", "weight": 40.0, "detail": "94% similarity with INV-SYS-001"},
                {"indicator": "repeat_invoice_num_risk", "weight": 30.0, "detail": "Invoice number INV-10025 already exists"}
            ],
            explanation="Potential risk detected — human review recommended."
        ))
        db.add(ReviewTask(
            invoice_id=inv3.id, status="PENDING", original_ai_decision="REVIEW",
            ai_risk_score=85.0, reason="High confidence duplicate transaction detected (94% similarity)"
        ))

        # Benchmark 4: Tax Mismatch Invoice
        inv4 = Invoice(
            invoice_id="INV-SYS-004",
            invoice_number="INV-30911",
            original_filename="invoice_4_tax_mismatch.pdf",
            file_type="PDF",
            file_path=str(settings.UPLOAD_DIR / "invoice_4_tax_mismatch.pdf"),
            file_size_bytes=155000,
            file_hash="bbbbbb1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126dbbbb",
            vendor_id=vendors_map["Delta Hardware & Systems"].id,
            po_id=po_map["PO-2026-088"].id,
            vendor_name_extracted="Delta Hardware & Systems",
            vendor_address_extracted="12 Industrial Area, Sector 5, Gurgaon",
            vendor_email_extracted="finance@deltasystems.in",
            vendor_tax_id_extracted="07DELAB5544P1Z3",
            invoice_date="2026-09-03",
            due_date="2026-09-25",
            currency="INR",
            payment_terms="Net 15",
            subtotal=80000.0,
            discount=0.0,
            tax_amount=22400.0,
            tax_percentage=28.0,
            total_amount=102400.0,
            bank_account_extracted="112233445566",
            bank_ifsc_extracted="SBIN0004567",
            status="review_required",
            final_decision="REVIEW",
            overall_confidence=0.95,
            risk_score=70.0,
            risk_level="HIGH",
            ai_recommendation="REVIEW",
            reasoning_summary="Tax discrepancy detected: expected 18% vs invoice 28% (diff: ₹8,000.00)",
            decision_reasons=[
                "Tax percentage 28.0% does not match configured tax rule (expected 18.0%)",
                "Tax amount ₹22,400.00 is higher than statutory expected tax ₹14,400.00"
            ],
            recommended_action="Verify vendor tax classification and require revised invoice before authorization.",
            processing_time_ms=1380
        )
        db.add(inv4)
        db.commit()
        db.refresh(inv4)

        db.add(InvoiceItem(
            invoice_id=inv4.id, description="Server Hardware Components",
            quantity=4.0, unit_price=20000.0, discount=0.0, tax_rate=28.0, tax_amount=22400.0,
            total_price=102400.0, confidence=0.96
        ))
        db.add(InvoiceValidation(
            invoice_id=inv4.id, required_fields_status="PASS", math_status="PASS",
            calculated_subtotal=80000.0, calculated_total=102400.0, invoice_total=102400.0,
            math_difference=0.0, math_notes="Calculations match.", tax_status="WARNING",
            tax_type="GST (CGST/SGST/IGST)", expected_tax_rate=18.0, detected_tax_rate=28.0,
            expected_tax_amount=14400.0, detected_tax_amount=22400.0, tax_difference=8000.0,
            tax_notes="Tax rate 28.0% deviates from expected rule of 18.0%.",
            po_match_status="PASS", po_number="PO-2026-088", po_discrepancies=[],
            duplicate_status="PASS", similarity_score=0.10, duplicate_notes="No duplicate detected."
        ))
        db.add(RiskAssessment(
            invoice_id=inv4.id, risk_score=70.0, risk_level="HIGH",
            unusual_tax_risk=True,
            anomalies_detected=[
                {"indicator": "unusual_tax_risk", "weight": 25.0, "detail": "Tax rate 28% exceeds standard 18% rate"}
            ],
            explanation="Potential risk detected — human review recommended."
        ))
        db.add(ReviewTask(
            invoice_id=inv4.id, status="PENDING", original_ai_decision="REVIEW",
            ai_risk_score=70.0, reason="Tax rate discrepancy: 28% billed vs 18% statutory schedule"
        ))

        # Seed initial Notifications
        notifs = [
            ("CRITICAL", "High-Risk Duplicate Detected", "Invoice INV-SYS-003 from ABC Technology matches existing record with 94% similarity.", 3),
            ("WARNING", "Purchase Order Quantity Mismatch", "Invoice INV-SYS-002 from XYZ Solutions exceeds PO quantity by 20 units.", 2),
            ("WARNING", "Tax Schedule Variance Flagged", "Invoice INV-SYS-004 has 28% GST applied instead of standard 18%.", 4),
            ("SUCCESS", "Invoice Auto-Approved", "Invoice INV-SYS-001 (ABC Technologies, ₹59,000) verified and auto-approved.", 1)
        ]
        for sev, title, msg, inv_ref_id in notifs:
            db.add(Notification(
                invoice_id=inv_ref_id,
                type=sev,
                title=title,
                message=msg,
                severity=sev,
                action_url=f"/invoices/{inv_ref_id}"
            ))

        db.commit()
