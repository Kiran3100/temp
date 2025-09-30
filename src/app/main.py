from fastapi import FastAPI, Request, Depends
from app.core.config import settings
from app.middlewares.tenant_middleware import TenantResolverMiddleware
from app.routers import auth, users, hostels, rooms, payments, complaints, beds
# from app.core.logging import configure_logging
import uvicorn
from app.db.engine import async_engine
from app.models.public import BasePublic
import asyncio
from sqlalchemy import text

configure_logging()

app = FastAPI(title=settings.APP_NAME)
app.add_middleware(TenantResolverMiddleware)

# mount routers


def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME)
    # install tenant middleware
    app.add_middleware(TenantResolverMiddleware)

    # include routers
    app.include_router(auth.router, prefix="/auth", tags=["auth"])
    app.include_router(users.router, prefix="/users", tags=["users"])
    app.include_router(hostels.router, prefix="/hostels", tags=["hostels"])
    app.include_router(rooms.router, prefix="/rooms", tags=["rooms"])
    app.include_router(payments.router, prefix="/payments", tags=["payments"])
    app.include_router(complaints.router, prefix="/complaints", tags=["complaints"])
    app.include_router(beds.router, prefix="/beds", tags=["beds"])

    @app.on_event("startup")
    async def startup():
        # ensure public schema tables exist for public models
        async with async_engine.begin() as conn:
            await conn.execute(text('CREATE SCHEMA IF NOT EXISTS public'))
            # set search_path to public and create public tables
            await conn.execute(text("SET search_path TO public"))
            def _create_public(sync_conn):
                BasePublic.metadata.create_all(bind=sync_conn)
            await conn.run_sync(_create_public)

    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
