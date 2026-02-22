import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserOut, UserUpdate, OnboardingRequest, UserStatsOut
from app.schemas.achievement import AchievementOut
from app.services.user_service import get_current_user
from app.redis_client import get_redis
import redis.asyncio as aioredis

router = APIRouter()

USER_CACHE_TTL = 300


@router.get("/me", response_model=UserOut)
async def get_me(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    cache_key = f"user:{user.id}:me"
    cached = await redis.get(cache_key)
    if cached:
        data = json.loads(cached)
        return data

    out = UserOut.model_validate(user)
    await redis.setex(cache_key, USER_CACHE_TTL, out.model_dump_json())
    return out


@router.patch("/me", response_model=UserOut)
async def update_me(
    body: UserUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    update_data = body.model_dump(exclude_none=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    await db.flush()
    await db.refresh(user)

    await redis.delete(f"user:{user.id}:me")

    return UserOut.model_validate(user)


@router.post("/me/onboarding", response_model=UserOut)
async def complete_onboarding(
    body: OnboardingRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    user.goals = body.goals
    user.mindset_profile = body.mindset_profile
    user.work_style = body.work_style
    user.activity_level = body.activity_level
    user.preferred_times = body.preferred_times
    user.onboarding_completed = True

    await db.flush()
    await db.refresh(user)

    await redis.delete(f"user:{user.id}:me")

    return UserOut.model_validate(user)


@router.get("/me/stats", response_model=UserStatsOut)
async def get_stats(user: User = Depends(get_current_user)):
    return UserStatsOut.model_validate(user)


@router.get("/me/achievements")
async def get_achievements(user: User = Depends(get_current_user)):
    sorted_achievements = sorted(user.achievements, key=lambda a: a.earned_at, reverse=True)
    return [AchievementOut.model_validate(a) for a in sorted_achievements]
