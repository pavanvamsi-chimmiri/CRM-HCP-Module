from datetime import UTC, datetime

from fastapi import APIRouter
from sqlalchemy import text

from app.api.deps import DbSession
from app.core.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.get("/health/ready")
async def readiness_check(db: DbSession) -> dict[str, str]:
    await db.execute(text("SELECT 1"))
    return {
        "status": "ready",
        "database": "connected",
        "timestamp": datetime.now(UTC).isoformat(),
    }
