from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.models import Vendor, Invoice
from backend.app.schemas.schemas import VendorOut

router = APIRouter(prefix="/vendors", tags=["Vendors"])

@router.get("", response_model=list[VendorOut])
def list_vendors(db: Session = Depends(get_db)):
    vendors = db.query(Vendor).order_by(Vendor.name).all()
    # Calculate fresh metrics
    for v in vendors:
        invs = db.query(Invoice).filter(Invoice.vendor_id == v.id).all()
        v.total_invoices_count = len(invs)
        if invs:
            v.historical_avg_amount = round(sum(i.total_amount for i in invs) / len(invs), 2)
    db.commit()
    return vendors

@router.get("/{id}", response_model=VendorOut)
def get_vendor_detail(id: int, db: Session = Depends(get_db)):
    vendor = db.query(Vendor).filter(Vendor.id == id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor

@router.get("/{id}/invoices")
def get_vendor_invoices(id: int, db: Session = Depends(get_db)):
    invoices = db.query(Invoice).filter(Invoice.vendor_id == id).order_by(Invoice.created_at.desc()).all()
    return [
        {
            "id": inv.id,
            "invoice_id": inv.invoice_id,
            "invoice_number": inv.invoice_number,
            "amount": inv.total_amount,
            "date": inv.invoice_date,
            "status": inv.status,
            "final_decision": inv.final_decision,
            "risk_score": inv.risk_score
        }
        for inv in invoices
    ]
