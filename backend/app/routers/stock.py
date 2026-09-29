from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from ..database import get_db
from .. import models

router = APIRouter()


@router.get("/stats")
def stats(db: Session = Depends(get_db)):
    return {
        "warehouses": db.query(func.count(models.Warehouse.id)).scalar() or 0,
        "products": db.query(func.count(models.Product.id)).scalar() or 0,
        "total_pieces": int(db.query(func.sum(models.Stock.balance_piece)).scalar() or 0),
        "negative_count": db.query(func.count(models.Stock.id)).filter(models.Stock.balance_piece < 0).scalar() or 0,
    }


@router.get("/central")
def central(product_search: Optional[str] = None, db: Session = Depends(get_db)):
    q = (db.query(
        models.Product.name,
        models.Product.pieces_per_carton,
        func.sum(models.Stock.balance_piece).label("total_piece"),
        func.count(func.distinct(models.Stock.warehouse_id)).label("wc"),
    ).join(models.Stock, models.Stock.product_id == models.Product.id)
     .group_by(models.Product.id, models.Product.name, models.Product.pieces_per_carton))
    if product_search:
        q = q.filter(models.Product.name.ilike(f"%{product_search}%"))
    out = []
    for name, ppc, total, wc in q.all():
        ppc = ppc or 0
        out.append({
            "product": name,
            "total_piece": int(total),
            "pieces_per_carton": ppc,
            "total_carton": round(total / ppc, 2) if ppc > 0 else 0,
            "warehouses_count": wc,
        })
    return out


@router.get("/negative")
def negative(db: Session = Depends(get_db)):
    rows = (db.query(models.Product.name, models.Warehouse.name, models.Stock.balance_piece)
            .join(models.Stock, models.Stock.product_id == models.Product.id)
            .join(models.Warehouse, models.Warehouse.id == models.Stock.warehouse_id)
            .filter(models.Stock.balance_piece < 0)
            .order_by(models.Stock.balance_piece.asc()).all())
    return [{"product": p, "warehouse": w, "balance": b} for p, w, b in rows]


@router.get("/warehouse/{name}")
def warehouse_stock(name: str, db: Session = Depends(get_db)):
    wh = db.query(models.Warehouse).filter_by(name=name).first()
    if not wh:
        raise HTTPException(404, "المخزن غير موجود")
    rows = (db.query(models.Product.name, models.Stock)
            .join(models.Stock, models.Stock.product_id == models.Product.id)
            .filter(models.Stock.warehouse_id == wh.id).all())
    items = [{"product": pn, "balance_piece": s.balance_piece,
              "balance_carton": float(s.balance_carton or 0),
              "pieces_per_carton": s.pieces_per_carton} for pn, s in rows]
    return {"warehouse": wh.name, "items_count": len(items),
            "total_pieces": sum(i["balance_piece"] for i in items), "items": items}


@router.get("/by-warehouse")
def by_warehouse(db: Session = Depends(get_db)):
    rows = (db.query(models.Warehouse.name, models.Warehouse.type,
                     func.sum(models.Stock.balance_piece).label("total"),
                     func.count(func.distinct(models.Stock.product_id)).label("pcount"))
            .join(models.Stock, models.Stock.warehouse_id == models.Warehouse.id)
            .group_by(models.Warehouse.id, models.Warehouse.name, models.Warehouse.type).all())
    return [{"warehouse": n, "type": t, "total_pieces": int(tot), "products": pc}
            for n, t, tot, pc in rows]
