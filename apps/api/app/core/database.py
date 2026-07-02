from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from .config import settings

DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://").replace(
    "postgres://", "postgresql+asyncpg://"
)

engine = create_async_engine(DATABASE_URL, echo=settings.DEBUG, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    import logging
    from sqlalchemy import text
    logger = logging.getLogger(__name__)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all, checkfirst=True)
            # Safe additive migrations — idempotent, never destructive
            for stmt in [
                "ALTER TABLE validators ADD COLUMN IF NOT EXISTS verified_claims JSONB",
                "ALTER TABLE validators ADD COLUMN IF NOT EXISTS disputed_claims JSONB",
            ]:
                try:
                    await conn.execute(text(stmt))
                except Exception as col_err:
                    logger.warning(f"Column migration skipped (safe): {col_err}")
    except Exception as e:
        # Two workers may race to create enum types on first boot — safe to ignore
        if "duplicate key" in str(e) or "already exists" in str(e):
            logger.warning(f"init_db race condition (safe to ignore): {e}")
        else:
            raise
