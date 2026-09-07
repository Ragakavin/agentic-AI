from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.app.database.session import get_db
from backend.app.models.models import Invoice, InvoiceReport
from backend.app.services.report_service import report_service

router = APIRouter(prefix="/reports", tags=["Reports"])

class ReportGenerateRequest(BaseModel):
    invoice_id: int
    format: str # "PDF", "EXCEL", or "CSV"

@router.post("/generate")
def generate_report(req: ReportGenerateRequest, db: Session = Depends(get_db)):
    inv = db.query(Invoice).filter(Invoice.id == req.invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")

    fmt = req.format.upper()
    if fmt == "PDF":
        path = report_service.generate_pdf_report(db, inv)
    elif fmt in ["EXCEL", "XLSX"]:
        path = report_service.generate_excel_report(db, inv)
    elif fmt == "CSV":
        path = report_service.generate_csv_report(db, inv)
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Supported: PDF, EXCEL, CSV")

    filename = Path(path).name
    return {
        "message": f"{fmt} report generated successfully.",
        "filename": filename,
        "download_url": f"/api/reports/download/{filename}"
    }

@router.get("/download/{filename}")
def download_report(filename: str):
    file_path = report_service.settings.REPORT_DIR / filename if hasattr(report_service, 'settings') else Path("reports") / filename
    if not file_path.exists():
        # Check absolute or default path
        from backend.app.core.config import settings
        file_path = settings.REPORT_DIR / filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Report file not found")

    media_types = {
        ".pdf": "application/pdf",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".csv": "text/csv"
    }
    media_type = media_types.get(file_path.suffix.lower(), "application/octet-stream")
    return FileResponse(path=str(file_path), filename=filename, media_type=media_type)

@router.get("/list")
def list_reports(db: Session = Depends(get_db)):
    reports = db.query(InvoiceReport).order_by(InvoiceReport.created_at.desc()).limit(30).all()
    return [
        {
            "id": r.id,
            "invoice_id": r.invoice_id,
            "invoice_ref": r.invoice.invoice_id if r.invoice else f"INV-{r.invoice_id}",
            "vendor_name": r.invoice.vendor_name_extracted if r.invoice else "Unknown",
            "report_type": r.report_type,
            "filename": Path(r.file_path).name,
            "file_size_bytes": r.file_size_bytes,
            "created_at": r.created_at,
            "download_url": f"/api/reports/download/{Path(r.file_path).name}"
        }
        for r in reports
    ]
