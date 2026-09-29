import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Load variables from a local .env file when running outside of Railway.
# In Railway, DATABASE_URL is already injected into the environment, so
# this is a no-op there.
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL environment variable is not set. "
        "Make sure a PostgreSQL service is attached to this app on Railway "
        "(or set DATABASE_URL locally in a .env file)."
    )

# Railway (and some providers) hand out URLs using the legacy "postgres://"
# scheme, which SQLAlchemy no longer accepts. Normalize it to "postgresql://".
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
