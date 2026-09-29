from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.sql import func
from .database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    full_name = Column(String(150))
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="viewer")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


class Warehouse(Base):
    __tablename__ = "warehouses"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    type = Column(String(20), nullable=False)
    canonical = Column(String(100))
    is_active = Column(Boolean, default=True)


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String(300), unique=True, nullable=False, index=True)
    pieces_per_carton = Column(Integer)
    category_guess = Column(String(100))
    is_active = Column(Boolean, default=True)


class Stock(Base):
    __tablename__ = "stock"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False)
    balance_piece = Column(Integer, nullable=False, default=0)
    balance_carton = Column(Numeric(12, 4), default=0)
    pieces_per_carton = Column(Integer)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Transfer(Base):
    __tablename__ = "transfers"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    from_warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    to_warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    status = Column(String(20), default="pending")
    user_id = Column(Integer, ForeignKey("users.id"))
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
