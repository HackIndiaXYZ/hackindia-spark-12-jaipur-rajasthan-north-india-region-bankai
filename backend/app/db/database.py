from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

db_url = settings.DATABASE_URL
connect_args = {}

if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    db_url,
    connect_args=connect_args,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from sqlalchemy import inspect, text
    import app.db.models  # Ensures all ORM models are registered on Base.metadata
    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)
    if "incidents" in inspector.get_table_names():
        existing_cols = {col["name"] for col in inspector.get_columns("incidents")}
        columns_to_add = [
            ("candidate_segments", "JSON"),
            ("responsive_sensors", "JSON"),
            ("acknowledged_at", "DATETIME"),
            ("resolved_at", "DATETIME"),
            ("peak_raw_adc", "INTEGER"),
            ("peak_pressure_equivalent", "FLOAT"),
            ("source", "VARCHAR DEFAULT 'LIVE HARDWARE'"),
            ("disclaimer", "TEXT")
        ]
        with engine.begin() as conn:
            for col_name, col_type in columns_to_add:
                if col_name not in existing_cols:
                    conn.execute(text(f"ALTER TABLE incidents ADD COLUMN {col_name} {col_type}"))

