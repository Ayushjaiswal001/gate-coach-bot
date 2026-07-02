"""Async engine/session factory. Alembic owns the prod schema; init_db() is for dev/tests."""

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from app.config import settings

_pg = settings.database_url.startswith("postgresql")
engine: AsyncEngine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=300,
    # Neon -pooler (PgBouncer) breaks asyncpg's prepared-statement cache — disable it.
    connect_args={"statement_cache_size": 0} if _pg else {},
)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def init_db() -> None:
    from app.db.models import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
