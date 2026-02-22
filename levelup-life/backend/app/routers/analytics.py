from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.services.user_service import get_current_user
from app.services.analytics_service import (
    get_summary,
    get_streak_data,
    get_weekly_report,
    get_patterns,
)
from app.redis_client import get_redis
import redis.asyncio as aioredis
import json

router = APIRouter()

ANALYTICS_SUMMARY_TTL = 3600


@router.get("/summary")
async def summary(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    cache_key = f"analytics:summary:{user.id}"
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)

    data = await get_summary(user.id, db)
    await redis.setex(cache_key, ANALYTICS_SUMMARY_TTL, json.dumps(data))
    return data


@router.get("/weekly-report")
async def weekly_report(
    week: str = Query(default=None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_weekly_report(user.id, week, db)


@router.get("/streaks")
async def streaks(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_streak_data(user.id, db)


@router.get("/patterns")
async def patterns(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_patterns(user.id, db)
