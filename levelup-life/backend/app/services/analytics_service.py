import uuid
from datetime import date, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.analytics import AnalyticsSnapshot
from app.models.quest import Quest


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
