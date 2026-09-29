from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas

router = APIRouter()


@router.post("/")
def create_transfer(payload: schemas.TransferCreate, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter_by(name=payload.product).first()
    if not product:
        raise HTTPException(404, "الصنف غير موجود")
    src = db.query(models.Warehouse).filter_by(name=payload.from_warehouse).first()
    dst = db.query(models.Warehouse).filter_by(name=payload.to_warehouse).first()
    if not src or not dst:
        raise HTTPException(404, "أحد المخازن غير موجود")
    src_stock = db.query(models.Stock).filter_by(product_id=product.id, warehouse_id=src.id).first()
    if not src_stock or src_stock.balance_piece < payload.quantity:
        raise HTTPException(400, "الرصيد غير كافٍ")
    src_stock.balance_piece -= payload.quantity
    dst_stock = db.query(models.Stock).filter_by(product_id=product.id, warehouse_id=dst.id).first()
    if dst_stock:
        dst_stock.balance_piece += payload.quantity
    else:
        db.add(models.Stock(product_id=product.id, warehouse_id=dst.id, balance_piece=payload.quantity))
    db.add(models.Transfer(product_id=product.id, from_warehouse_id=src.id,
                            to_warehouse_id=dst.id, quantity=payload.quantity, status="completed"))
    db.commit()
    return {"status": "ok"}


@router.get("/")
def list_transfers(db: Session = Depends(get_db)):
    rows = db.query(models.Transfer).order_by(models.Transfer.created_at.desc()).limit(100).all()
    return [{"id": t.id, "product_id": t.product_id, "from_id": t.from_warehouse_id,
             "to_id": t.to_warehouse_id, "quantity": t.quantity, "status": t.status,
             "created_at": t.created_at} for t in rows]
