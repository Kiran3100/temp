from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from app.core.config import settings
from app.models.public import BasePublic
from app.models.tenant import TenantBase

engine = create_engine(
    settings.DATABASE_URL.replace("+asyncpg", ""),  # use psycopg2
    pool_pre_ping=True,
    pool_size=getattr(settings, "DB_POOL_SIZE", 10),
    max_overflow=getattr(settings, "DB_MAX_OVERFLOW", 20),
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db(tenant_schema: str | None = None):
    db = SessionLocal()
    try:
        if tenant_schema:
            db.execute(text(f'SET search_path TO "{tenant_schema}", public'))
        else:
            db.execute(text("SET search_path TO public"))
        yield db
    finally:
        db.close()

def provision_tenant_schema(tenant_schema: str):
    with engine.begin() as conn:
        conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{tenant_schema}"'))
        conn.execute(text(f"SET search_path TO {tenant_schema}, public"))
        TenantBase.metadata.create_all(bind=conn)
