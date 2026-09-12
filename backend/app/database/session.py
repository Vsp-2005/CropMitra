"""
Database session and connection management for CropMitra.
Supports SQLite out of the box and PostgreSQL via DATABASE_URL.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cropmitra.db")

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def run_migrations():
    """Safely adds new columns if they do not exist in the database."""
    from sqlalchemy import inspect, text
    inspector = inspect(engine)
    if "recommendations" in inspector.get_table_names():
        columns = [c["name"] for c in inspector.get_columns("recommendations")]
        with engine.begin() as conn:
            if "state" not in columns:
                conn.execute(text("ALTER TABLE recommendations ADD COLUMN state VARCHAR(100)"))
            if "district" not in columns:
                conn.execute(text("ALTER TABLE recommendations ADD COLUMN district VARCHAR(100)"))
            if "location_match_level" not in columns:
                conn.execute(text("ALTER TABLE recommendations ADD COLUMN location_match_level VARCHAR(50) DEFAULT 'district'"))
            if "model_score" not in columns:
                conn.execute(text("ALTER TABLE recommendations ADD COLUMN model_score FLOAT"))
            if "ml_score" not in columns:
                conn.execute(text("ALTER TABLE recommendations ADD COLUMN ml_score FLOAT"))
            if "final_score" not in columns:
                conn.execute(text("ALTER TABLE recommendations ADD COLUMN final_score FLOAT"))
            if "model_version" not in columns:
                conn.execute(text("ALTER TABLE recommendations ADD COLUMN model_version VARCHAR(50) DEFAULT '2.0.0'"))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
