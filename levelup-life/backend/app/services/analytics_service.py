import uuid
from datetime import date, timedelta, datetime
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.analytics import AnalyticsSnapshot
from app.models.quest import Quest
from sqlalchemy.orm import selectinload


async def get_summary(user_id: uuid.UUID, db: AsyncSession) -> dict:
    today = date.today()
    week_start = today - timedelta(days=7)

    week_result = await db.execute(
        select(
            func.count(Quest.id).label("count"),
            func.sum(Quest.xp_reward).label("xp"),
        ).where(
            Quest.user_id == user_id,
            Quest.is_completed == True,
            Quest.quest_date >= week_start,
        )
    )
    week_row = week_result.one()

    all_result = await db.execute(
        select(
            func.count(Quest.id).label("count"),
            func.sum(Quest.xp_reward).label("xp"),
        ).where(Quest.user_id == user_id, Quest.is_completed == True)
    )
    all_row = all_result.one()

    domain_result = await db.execute(
        select(Quest.domain, func.count(Quest.id)).where(
            Quest.user_id == user_id, Quest.is_completed == True
        ).group_by(Quest.domain)
    )
    domain_dist = {row[0].value: row[1] for row in domain_result.all()}

    return {
        "this_week": {
            "quests_completed": week_row.count or 0,
            "xp_earned": int(week_row.xp or 0),
        },
        "all_time": {
            "quests_completed": all_row.count or 0,
            "xp_earned": int(all_row.xp or 0),
        },
        "domain_distribution": domain_dist,
    }


async def get_streak_data(user_id: uuid.UUID, db: AsyncSession) -> list:
    today = date.today()
    start = today - timedelta(days=89)

    result = await db.execute(
        select(Quest.quest_date, func.count(Quest.id).label("count"))
        .where(
            Quest.user_id == user_id,
            Quest.is_completed == True,
            Quest.quest_date >= start,
        )
        .group_by(Quest.quest_date)
        .order_by(Quest.quest_date)
    )

    data_map = {row.quest_date: row.count for row in result.all()}
    streak_data = []
    for i in range(90):
        d = start + timedelta(days=i)
        streak_data.append({"date": d.isoformat(), "completed_count": data_map.get(d, 0)})
    return streak_data


async def get_weekly_report(user_id: uuid.UUID, week: str | None, db: AsyncSession) -> dict:
    """Get weekly report with AI insights."""
    today = date.today()

    if week:
        try:
            week_date = datetime.strptime(week, "%Y-%W").date()
        except ValueError:
            week_date = today - timedelta(days=today.weekday())
    else:
        week_date = today - timedelta(days=today.weekday())

    week_start = week_date
    week_end = week_date + timedelta(days=6)

    result = await db.execute(
        select(
            func.count(Quest.id).label("total"),
            func.sum(Quest.xp_reward).label("xp"),
            Quest.domain,
        )
        .where(
            Quest.user_id == user_id,
            Quest.is_completed == True,
            and_(Quest.quest_date >= week_start, Quest.quest_date <= week_end),
        )
        .group_by(Quest.domain)
    )

    rows = result.all()
    metrics = {}
    total_completed = 0
    total_xp = 0

    for row in rows:
        metrics[row.domain.value] = {
            "completed": row.total or 0,
            "xp": int(row.xp or 0),
        }
        total_completed += row.total or 0
        total_xp += row.xp or 0

    metrics["total"] = {"completed": total_completed, "xp": total_xp}

    # Get AI insights from snapshot
    snapshot_result = await db.execute(
        select(AnalyticsSnapshot).where(
            and_(
                AnalyticsSnapshot.user_id == user_id,
                AnalyticsSnapshot.snapshot_date == week_start,
            )
        )
    )
    snapshot = snapshot_result.scalar_one_or_none()

    insights = snapshot.ai_insights if snapshot else None

    return {
        "week": week_date.strftime("%Y-%W"),
        "week_start": week_start.isoformat(),
        "week_end": week_end.isoformat(),
        "metrics": metrics,
        "insights": insights or "No insights available for this week.",
    }


async def get_patterns(user_id: uuid.UUID, db: AsyncSession) -> dict:
    """Analyze user patterns including best day, time, top domain, and completion rate trend."""
    today = date.today()
    last_30_days = today - timedelta(days=30)

    # Best day of week
    day_result = await db.execute(
        select(func.extract("dow", Quest.quest_date).label("day"), func.count(Quest.id).label("count"))
        .where(
            Quest.user_id == user_id,
            Quest.is_completed == True,
            Quest.quest_date >= last_30_days,
        )
        .group_by(func.extract("dow", Quest.quest_date))
        .order_by(func.count(Quest.id).desc())
    )

    day_row = day_result.first()
    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    best_day = days[int(day_row.day)] if day_row else None

    # Top domain
    domain_result = await db.execute(
        select(Quest.domain, func.count(Quest.id).label("count"))
        .where(
            Quest.user_id == user_id,
            Quest.is_completed == True,
            Quest.quest_date >= last_30_days,
        )
        .group_by(Quest.domain)
        .order_by(func.count(Quest.id).desc())
    )

    domain_row = domain_result.first()
    top_domain = domain_row.domain.value if domain_row else None

    # Completion rate trend (last 4 weeks vs previous 4 weeks)
    mid_point = today - timedelta(days=14)

    recent_result = await db.execute(
        select(func.count(Quest.id))
        .where(
            Quest.user_id == user_id,
            Quest.quest_date >= mid_point,
        )
    )
    recent_completed = await db.execute(
        select(func.count(Quest.id))
        .where(
            Quest.user_id == user_id,
            Quest.is_completed == True,
            Quest.quest_date >= mid_point,
        )
    )

    earlier_result = await db.execute(
        select(func.count(Quest.id))
        .where(
            Quest.user_id == user_id,
            and_(Quest.quest_date >= last_30_days, Quest.quest_date < mid_point),
        )
    )
    earlier_completed = await db.execute(
        select(func.count(Quest.id))
        .where(
            Quest.user_id == user_id,
            Quest.is_completed == True,
            and_(Quest.quest_date >= last_30_days, Quest.quest_date < mid_point),
        )
    )

    recent_total = recent_result.scalar() or 0
    recent_done = recent_completed.scalar() or 0
    earlier_total = earlier_result.scalar() or 0
    earlier_done = earlier_completed.scalar() or 0

    recent_rate = recent_done / recent_total if recent_total > 0 else 0
    earlier_rate = earlier_done / earlier_total if earlier_total > 0 else 0

    completion_rate_trend = round((recent_rate - earlier_rate) * 100, 1) if earlier_total > 0 else 0

    return {
        "best_day": best_day,
        "best_time": None,  # Would require hour-level completion data
        "top_domain": top_domain,
        "completion_rate_trend": completion_rate_trend,
    }
