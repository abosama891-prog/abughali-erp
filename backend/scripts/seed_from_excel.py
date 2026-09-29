import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from app.database import SessionLocal, engine, Base
from app import models
from app.auth import hash_password

EXCEL = "AbuGhali_ERP_With_Import.xlsx"


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # المخازن
    print("📦 المخازن...")
    df = pd.read_excel(EXCEL, sheet_name="المخازن 22")
    for _, r in df.iterrows():
        if not db.query(models.Warehouse).filter_by(id=int(r["id"])).first():
            db.add(models.Warehouse(
                id=int(r["id"]),
                name=str(r["name"]).strip(),
                type=str(r["type"]).strip(),
                canonical=str(r.get("canonical", "")) if pd.notna(r.get("canonical")) else None,
            ))
    db.commit()
    print(f"   ✅ {db.query(models.Warehouse).count()} مخزن")

    # الأصناف
    print("📦 الأصناف...")
    df = pd.read_excel(EXCEL, sheet_name="الأصناف 1509")
    for _, r in df.iterrows():
        name = str(r["name"]).strip()
        if not name or name == "nan":
            continue
        ppc = None
        if pd.notna(r.get("pieces_per_carton")):
            try:
                ppc = int(r["pieces_per_carton"])
            except:
                pass
        if not db.query(models.Product).filter_by(id=int(r["id"])).first():
            db.add(models.Product(
                id=int(r["id"]),
                name=name,
                pieces_per_carton=ppc,
                category_guess=str(r.get("category_guess", "")) if pd.notna(r.get("category_guess")) else None,
            ))
    db.commit()
    print(f"   ✅ {db.query(models.Product).count()} صنف")

    # الأرصدة
    print("📦 الأرصدة...")
    df = pd.read_excel(EXCEL, sheet_name="الأرصدة النظيفة")
    wh_map = {w.name: w.id for w in db.query(models.Warehouse).all()}
    pr_map = {p.name: p.id for p in db.query(models.Product).all()}
    count = 0
    for _, r in df.iterrows():
        pname = str(r["product"]).strip()
        wname = str(r["warehouse"]).strip()
        if pname.startswith("اجمالى") or pname == "الاجمالى":
            continue
        if pname not in pr_map or wname not in wh_map:
            continue
        try:
            piece = int(r["balance_piece"])
        except:
            continue
        carton = float(r["balance_carton"]) if pd.notna(r["balance_carton"]) else 0
        ppc = None
        if pd.notna(r.get("pieces_per_carton")):
            try:
                ppc = int(r["pieces_per_carton"])
            except:
                pass
        existing = db.query(models.Stock).filter_by(
            product_id=pr_map[pname], warehouse_id=wh_map[wname]
        ).first()
        if existing:
            existing.balance_piece = piece
            existing.balance_carton = carton
            existing.pieces_per_carton = ppc
        else:
            db.add(models.Stock(
                product_id=pr_map[pname],
                warehouse_id=wh_map[wname],
                balance_piece=piece,
                balance_carton=carton,
                pieces_per_carton=ppc,
            ))
        count += 1
    db.commit()
    print(f"   ✅ {count} رصيد")

    # Admin
    if not db.query(models.User).filter_by(username="admin").first():
        db.add(models.User(
            username="admin",
            full_name="مدير النظام",
            hashed_password=hash_password("Admin@2026"),
            role="admin",
        ))
        db.commit()
        print("   ✅ admin / Admin@2026")

    print("\n🎉 تم!")
    db.close()


if __name__ == "__main__":
    seed()
