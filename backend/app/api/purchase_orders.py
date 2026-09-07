from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.models import PurchaseOrder, PurchaseOrderItem
from backend.app.schemas.schemas import PurchaseOrderOut, POItemOut

router = APIRouter(prefix="/purchase-orders", tags=["Purchase Orders"])

@router.get("", response_model=list[PurchaseOrderOut])
def list_purchase_orders(db: Session = Depends(get_db)):
    pos = db.query(PurchaseOrder).order_by(PurchaseOrder.order_date.desc()).all()
    res = []
    for po in pos:
        items = [
            POItemOut(
                id=it.id,
                item_description=it.item_description,
                quantity=it.quantity,
                unit_price=it.unit_price,
                tax_rate=it.tax_rate,
                total_price=it.total_price
            )
            for it in po.items
        ]
        res.append(PurchaseOrderOut(
            id=po.id,
            po_number=po.po_number,
            vendor_id=po.vendor_id,
            vendor_name=po.vendor.name if po.vendor else None,
            order_date=po.order_date,
            currency=po.currency,
            subtotal=po.subtotal,
            tax_amount=po.tax_amount,
            total_amount=po.total_amount,
            status=po.status,
            items=items
        ))
    return res

@router.get("/{id}", response_model=PurchaseOrderOut)
def get_purchase_order(id: int, db: Session = Depends(get_db)):
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == id).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase Order not found")
    
    items = [
        POItemOut(
            id=it.id,
            item_description=it.item_description,
            quantity=it.quantity,
            unit_price=it.unit_price,
            tax_rate=it.tax_rate,
            total_price=it.total_price
        )
        for it in po.items
    ]
    return PurchaseOrderOut(
        id=po.id,
        po_number=po.po_number,
        vendor_id=po.vendor_id,
        vendor_name=po.vendor.name if po.vendor else None,
        order_date=po.order_date,
        currency=po.currency,
        subtotal=po.subtotal,
        tax_amount=po.tax_amount,
        total_amount=po.total_amount,
        status=po.status,
        items=items
    )
