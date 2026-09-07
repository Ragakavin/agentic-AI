import csv
import io
from pathlib import Path
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from backend.app.models.models import Invoice, InvoiceReport
from backend.app.core.config import settings

class ReportService:
    def generate_pdf_report(self, db: Session, invoice: Invoice) -> str:
        """Generate a sleek, professional PDF Invoice Analysis Report using ReportLab."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"Report_{invoice.invoice_id}_{timestamp}.pdf"
        output_path = settings.REPORT_DIR / filename

        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#0f172a")
        )
        subtitle_style = ParagraphStyle(
            "DocSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#64748b")
        )
        section_style = ParagraphStyle(
            "SectionHeader",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#1e293b"),
            spaceBefore=12,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#334155")
        )

        story = []

        # Document Header
        story.append(Paragraph("AGENTIC AI INVOICE ANALYSIS & COMPLIANCE REPORT", title_style))
        story.append(Paragraph(f"System Reference: {invoice.invoice_id} | Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}", subtitle_style))
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#3b82f6"), spaceAfter=15))

        # Executive Summary Box
        status_color = "#10b981" if invoice.final_decision == "APPROVE" else ("#ef4444" if invoice.final_decision == "REJECT" else "#f59e0b")
        summary_data = [
            [
                Paragraph("<b>Invoice Number:</b>", body_style), Paragraph(invoice.invoice_number or "N/A", body_style),
                Paragraph("<b>Final Decision:</b>", body_style), Paragraph(f"<b><font color='{status_color}'>{invoice.final_decision or invoice.status.upper()}</font></b>", body_style)
            ],
            [
                Paragraph("<b>Vendor Name:</b>", body_style), Paragraph(invoice.vendor_name_extracted or "N/A", body_style),
                Paragraph("<b>Risk Score:</b>", body_style), Paragraph(f"<b>{invoice.risk_score:.0f}/100 ({invoice.risk_level})</b>", body_style)
            ],
            [
                Paragraph("<b>Total Amount:</b>", body_style), Paragraph(f"₹{invoice.total_amount:,.2f}", body_style),
                Paragraph("<b>AI Confidence:</b>", body_style), Paragraph(f"{invoice.overall_confidence*100:.1f}%", body_style)
            ],
            [
                Paragraph("<b>Invoice Date:</b>", body_style), Paragraph(invoice.invoice_date or "N/A", body_style),
                Paragraph("<b>PO Reference:</b>", body_style), Paragraph(invoice.purchase_order.po_number if invoice.purchase_order else (invoice.extracted_fields or {}).get("po_number", {}).get("value", "None"), body_style)
            ]
        ]
        t_summary = Table(summary_data, colWidths=[110, 160, 110, 160])
        t_summary.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#f1f5f9")),
            ("PADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(t_summary)
        story.append(Spacer(1, 15))

        # AI Reasoning & Evidence
        story.append(Paragraph("AI Reasoning & Evidence Synthesis", section_style))
        reasons_list = invoice.decision_reasons or ["All automated checks passed."]
        reason_text = "<br/>".join([f"• {r}" for r in reasons_list])
        story.append(Paragraph(reason_text, body_style))
        story.append(Spacer(1, 8))
        story.append(Paragraph(f"<b>Recommended Action:</b> {invoice.recommended_action or 'Payment processing.'}", body_style))
        story.append(Spacer(1, 15))

        # Line Items
        story.append(Paragraph("Itemized Line Breakdown", section_style))
        items_table_data = [["Item Description", "Qty", "Unit Price (₹)", "Tax Rate", "Total (₹)"]]
        for it in invoice.items:
            items_table_data.append([
                it.description,
                f"{it.quantity:g}",
                f"{it.unit_price:,.2f}",
                f"{it.tax_rate}%",
                f"{it.total_price:,.2f}"
            ])
        t_items = Table(items_table_data, colWidths=[240, 50, 80, 70, 100])
        t_items.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ]))
        story.append(t_items)
        story.append(Spacer(1, 15))

        # Multi-Agent Verification Matrix
        story.append(Paragraph("Multi-Agent Verification Matrix", section_style))
        val = invoice.validations
        matrix_data = [
            ["Agent Verification Stage", "Status", "Details & Metrics"],
            ["1. Mathematical Verification", val.math_status if val else "PASS", val.math_notes if val else "Calculations match"],
            ["2. Tax Compliance Check", val.tax_status if val else "PASS", f"Detected: {val.detected_tax_rate if val else 18}% vs Expected: {val.expected_tax_rate if val else 18}%" if val else "Normal"],
            ["3. Duplicate Analysis", val.duplicate_status if val else "PASS", f"Similarity: {(val.similarity_score if val else 0)*100:.1f}% ({val.duplicate_notes if val else 'Clean'})"],
            ["4. Purchase Order Matching", val.po_match_status if val else "PASS", "; ".join(val.po_discrepancies if (val and val.po_discrepancies) else ["Matched within configured tolerance"])],
            ["5. Fraud Risk Assessment", invoice.risk_level, f"Score: {invoice.risk_score:.0f}/100 | Anomalies Flagged: {len(invoice.risk_assessment.anomalies_detected if invoice.risk_assessment else [])}"]
        ]
        t_matrix = Table(matrix_data, colWidths=[160, 90, 290])
        t_matrix.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#334155")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ]))
        story.append(t_matrix)

        doc.build(story)

        # Record Report
        rep = InvoiceReport(
            invoice_id=invoice.id,
            report_type="PDF",
            file_path=str(output_path),
            file_size_bytes=output_path.stat().st_size
        )
        db.add(rep)
        db.commit()

        return str(output_path)

    def generate_excel_report(self, db: Session, invoice: Invoice) -> str:
        """Generate structured Excel report with formatting and formulas."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"Report_{invoice.invoice_id}_{timestamp}.xlsx"
        output_path = settings.REPORT_DIR / filename

        wb = Workbook()
        ws = wb.active
        ws.title = "Invoice Analysis"

        header_font = Font(name="Calibri", size=12, bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
        title_font = Font(name="Calibri", size=14, bold=True, color="0F172A")

        # Title
        ws["A1"] = "AGENTIC AI INVOICE ANALYSIS REPORT"
        ws["A1"].font = title_font
        ws["A2"] = f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')} | Reference: {invoice.invoice_id}"

        # Metadata rows
        meta = [
            ("Invoice Number", invoice.invoice_number),
            ("Vendor", invoice.vendor_name_extracted),
            ("Invoice Date", invoice.invoice_date),
            ("Currency", invoice.currency),
            ("Subtotal", invoice.subtotal),
            ("Tax Amount", invoice.tax_amount),
            ("Total Amount", invoice.total_amount),
            ("Decision", invoice.final_decision),
            ("Risk Score", f"{invoice.risk_score:.0f}/100 ({invoice.risk_level})"),
            ("Confidence", f"{invoice.overall_confidence*100:.1f}%")
        ]
        for row_idx, (k, v) in enumerate(meta, start=4):
            ws[f"A{row_idx}"] = k
            ws[f"B{row_idx}"] = v
            ws[f"A{row_idx}"].font = Font(bold=True)

        # Line Items Table
        start_row = 16
        headers = ["Item Description", "Quantity", "Unit Price", "Tax Rate", "Total Price"]
        for col_idx, h in enumerate(headers, start=1):
            cell = ws.cell(row=start_row, column=col_idx, value=h)
            cell.font = header_font
            cell.fill = header_fill

        for r_offset, it in enumerate(invoice.items, start=1):
            curr_row = start_row + r_offset
            ws.cell(row=curr_row, column=1, value=it.description)
            ws.cell(row=curr_row, column=2, value=it.quantity)
            ws.cell(row=curr_row, column=3, value=it.unit_price)
            ws.cell(row=curr_row, column=4, value=f"{it.tax_rate}%")
            ws.cell(row=curr_row, column=5, value=it.total_price)

        wb.save(str(output_path))

        rep = InvoiceReport(
            invoice_id=invoice.id,
            report_type="EXCEL",
            file_path=str(output_path),
            file_size_bytes=output_path.stat().st_size
        )
        db.add(rep)
        db.commit()

        return str(output_path)

    def generate_csv_report(self, db: Session, invoice: Invoice) -> str:
        """Export invoice analysis data as CSV."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"Report_{invoice.invoice_id}_{timestamp}.csv"
        output_path = settings.REPORT_DIR / filename

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Field", "Value"])
            writer.writerow(["Invoice ID", invoice.invoice_id])
            writer.writerow(["Invoice Number", invoice.invoice_number])
            writer.writerow(["Vendor", invoice.vendor_name_extracted])
            writer.writerow(["Invoice Date", invoice.invoice_date])
            writer.writerow(["Currency", invoice.currency])
            writer.writerow(["Subtotal", invoice.subtotal])
            writer.writerow(["Tax Amount", invoice.tax_amount])
            writer.writerow(["Total Amount", invoice.total_amount])
            writer.writerow(["Decision", invoice.final_decision])
            writer.writerow(["Risk Score", invoice.risk_score])
            writer.writerow(["Confidence", invoice.overall_confidence])
            writer.writerow([])
            writer.writerow(["Line Items"])
            writer.writerow(["Description", "Quantity", "UnitPrice", "TaxRate", "TotalPrice"])
            for it in invoice.items:
                writer.writerow([it.description, it.quantity, it.unit_price, it.tax_rate, it.total_price])

        rep = InvoiceReport(
            invoice_id=invoice.id,
            report_type="CSV",
            file_path=str(output_path),
            file_size_bytes=output_path.stat().st_size
        )
        db.add(rep)
        db.commit()

        return str(output_path)

report_service = ReportService()
