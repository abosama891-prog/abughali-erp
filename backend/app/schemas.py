from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    full_name: Optional[str]


class UserCreate(BaseModel):
    username: str
    full_name: Optional[str] = None
    password: str
    role: str = "viewer"


class UserOut(BaseModel):
    id: int
    username: str
    full_name: Optional[str]
    role: str
    is_active: bool
    class Config:
        from_attributes = True


class WarehouseOut(BaseModel):
    id: int
    name: str
    type: str
    canonical: Optional[str]
    is_active: bool
    class Config:
        from_attributes = True


class ProductOut(BaseModel):
    id: int
    name: str
    pieces_per_carton: Optional[int]
    category_guess: Optional[str]
    class Config:
        from_attributes = True


class TransferCreate(BaseModel):
    product: str
    from_warehouse: str
    to_warehouse: str
    quantity: int
    notes: Optional[str] = None
