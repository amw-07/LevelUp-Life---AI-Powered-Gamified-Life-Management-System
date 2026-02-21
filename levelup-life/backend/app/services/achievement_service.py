import uuid
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.achievement import Achievement

ACHIEVEMENT_DEFINITIONS = [
    {
        "key": "first_quest",
        "name": "First Steps",
        "icon": "🎯",
        "desc": "Completed first quest",
        "fn": lambda q, s, x: q >= 1,
    },
    {
        "key": "ten_quests",
        "name": "Getting Started",
        "icon": "⚔️",
        "desc": "Completed 10 quests",
        "fn": lambda q, s, x: q >= 10,
    },
    {
        "key": "fifty_quests",
        "name": "Quest Master",
        "icon": "🗡️",
        "desc": "Completed 50 quests",
        "fn": lambda q, s, x: q >= 50,
    },
    {
        "key": "hundred_quests",
        "name": "Legendary Hero",
        "icon": "👑",
        "desc": "Completed 100 quests",
        "fn": lambda q, s, x: q >= 100,
    },
    {
        "key": "week_warrior",
        "name": "Week Warrior",
        "icon": "🔥",
        "desc": "7-day streak",
        "fn": lambda q, s, x: s >= 7,
    },
    {
        "key": "month_master",
        "name": "Monthly Master",
        "icon": "💪",
        "desc": "30-day streak",
        "fn": lambda q, s, x: s >= 30,
    },
    {
        "key": "xp_collector",
        "name": "XP Collector",
        "icon": "⭐",
        "desc": "Earned 10,000 XP",
        "fn": lambda q, s, x: x >= 10000,
    },
    {
        "key": "xp_hoarder",
        "name": "XP Hoarder",
        "icon": "💰",
        "desc": "Earned 50,000 XP",
        "fn": lambda q, s, x: x >= 50000,
    },
]


async def check_and_award(
    user_id: uuid.UUID,
    new_xp: int,
    new_streak: int,
    new_quest_count: int,
    db: AsyncSession,
) -> List[Achievement]:
    result = await db.execute(
        select(Achievement.key).where(Achievement.user_id == user_id)
    )
    claimed = set(result.scalars().all())

    new_achievements = []
    for defn in ACHIEVEMENT_DEFINITIONS:
        if defn["key"] not in claimed and defn["fn"](new_quest_count, new_streak, new_xp):
            ach = Achievement(
                user_id=user_id,
                key=defn["key"],
                name=defn["name"],
                icon=defn["icon"],
                description=defn["desc"],
            )
            db.add(ach)
            new_achievements.append(ach)

    if new_achievements:
        await db.flush()

    return new_achievements
