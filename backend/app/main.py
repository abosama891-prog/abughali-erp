from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import auth, warehouses, products, stock, transfers

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AbuGhali ERP API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,        prefix="/api/auth",       tags=["Auth"])
app.include_router(warehouses.router,  prefix="/api/warehouses", tags=["Warehouses"])
app.include_router(products.router,    prefix="/api/products",   tags=["Products"])
app.include_router(stock.router,       prefix="/api/stock",      tags=["Stock"])
app.include_router(transfers.router,   prefix="/api/transfers",  tags=["Transfers"])


@app.get("/")
def root():
    return {"app": "AbuGhali ERP", "status": "running", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "healthy"}
