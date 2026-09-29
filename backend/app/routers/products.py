from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from .. import models, schemas

router = APIRouter()


@router.get("/", response_model=list[schemas.ProductOut])
def list_products(
    search: Optional[str] = None,
    limit: int = Query(100, le=2000),
    db: Session = Depends(get_db),
):
    q = db.query(models.Product)
    if search:
        q = q.filter(models.Product.name.ilike(f"%{search}%"))
    return q.order_by(models.Product.name).limit(limit).all()
