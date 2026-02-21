from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.services.user_service import get_current_user
from app.services.analytics_service import get_summary, get_streak_data

router = APIRouter()


@router.get("/summary")
async def summary(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_summary(user.id, db)


@router.get("/weekly-report")
async def weekly_report(
    week: str = Query(default=None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return {"week": week, "insights": "Weekly AI report coming soon.", "metrics": {}}


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
    return {
        "best_day": None,
        "best_time": None,
        "top_domain": None,
        "completion_rate_trend": None,
    }
