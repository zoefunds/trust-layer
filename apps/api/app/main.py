import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .core.config import settings
from .core.database import init_db
from .core.redis import close_redis
from .routers import auth, investigations

if settings.SENTRY_DSN:
    sentry_sdk.init(dsn=settings.SENTRY_DSN, traces_sample_rate=0.1)


async def _cleanup_stale_investigations():
    """Mark investigations stuck in 'running' for >15 minutes as 'failed'."""
    import logging
    from datetime import datetime, timezone, timedelta
    from sqlalchemy import select, update
    from .models.investigation import Investigation
    from .core.database import AsyncSessionLocal

    logger = logging.getLogger(__name__)
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=15)
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                update(Investigation)
                .where(Investigation.status == "running", Investigation.created_at < cutoff)
                .values(status="failed")
                .returning(Investigation.id)
            )
            stale_ids = [row[0] for row in result.fetchall()]
            if stale_ids:
                await db.commit()
                logger.info(f"[Cleanup] Marked {len(stale_ids)} stale investigations as failed: {stale_ids}")
    except Exception as e:
        logger.error(f"[Cleanup] Failed to clean stale investigations: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await _cleanup_stale_investigations()
    yield
    await close_redis()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(investigations.router)


@app.get("/health")
async def health():
    return {"status": "ok", "version": settings.APP_VERSION}


@app.get("/reports/{investigation_id}")
async def get_report_redirect(investigation_id: str):
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=f"/investigations/{investigation_id}")
