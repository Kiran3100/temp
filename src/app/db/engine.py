# src/app/db/engine.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from app.core.config import settings

# Async engine used for both public and tenant work. We'll set search_path per-session.
async_engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,  
    echo=True,
    pool_pre_ping=True,
)