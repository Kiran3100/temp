from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from contextlib import contextmanager
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import AsyncGenerator, Optional
from app.db.engine import async_engine
from app.models.public import BasePublic  # for public metadata
from app.models.tenant import TenantBase

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
@contextmanager
def get_db(tenant_schema: str | None = None):
    db = SessionLocal()
    try:
        if tenant_schema:
            # Use parameterized query to prevent SQL injection
            # Note: schema names can't be parameterized, so validate input
            if not tenant_schema.replace('_', '').isalnum():
                raise ValueError("Invalid schema name")
            db.execute(text("SET search_path TO :schema, public").bindparams(schema=tenant_schema))
        yield db
    finally:
        db.close()

@asynccontextmanager
async def get_tenant_db(tenant_schema: Optional[str]) -> AsyncGenerator[AsyncSession, None]:
    if not tenant_schema:
        raise RuntimeError("Tenant schema not provided")
    
    # Validate schema name
    if not tenant_schema.replace('_', '').isalnum():
        raise ValueError("Invalid schema name")
    
    async with AsyncSessionLocal() as session:
        # PostgreSQL doesn't support bind parameters for SET search_path
        # Validate the schema name exists before setting
        result = await session.execute(
            text("SELECT schema_name FROM information_schema.schemata WHERE schema_name = :schema"),
            {"schema": tenant_schema}
        )
        if not result.scalar():
            raise ValueError(f"Schema {tenant_schema} does not exist")
        
        await session.execute(text(f"SET search_path TO {tenant_schema}, public"))
        yield session


@asynccontextmanager
async def get_public_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide an AsyncSession that uses the public schema.
    """
    async with AsyncSessionLocal() as session:
        # ensure search_path set to public
        await session.execute(text("SET search_path TO public"))
        yield session


# Helper to provision tenant (create schema + create tenant tables)
async def provision_tenant_schema(tenant_schema: str):
    async with async_engine.begin() as conn:
        # create schema if not exists
        await conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{tenant_schema}"'))
        # set search path and create tables for tenant metadata
        await conn.execute(text(f"SET search_path TO {tenant_schema}, public"))
        # use run_sync to call metadata.create_all on sync connection
        def _create_all(sync_conn):
            TenantBase.metadata.create_all(bind=sync_conn)

        await conn.run_sync(_create_all)
