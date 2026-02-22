import uuid
from datetime import datetime, timezone, date
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.models.quest import Quest
from app.models.user import User
from app.schemas.quest import QuestCreate, CompletionResult
from app.utils.game_mechanics import get_rank_from_xp, get_level_from_xp, calculate_streak
from app.services import achievement_service


async def get_quests_for_today(user_id: uuid.UUID, db: AsyncSession) -> List[Quest]:
    today = date.today()
    result = await db.execute(
        select(Quest).where(Quest.user_id == user_id, Quest.quest_date == today)
    )
    return result.scalars().all()


async def create_quest(user_id: uuid.UUID, quest_data: QuestCreate, db: AsyncSession) -> Quest:
    today = date.today()
    quest = Quest(
        user_id=user_id,
        title=quest_data.title,
        description=quest_data.description,
        domain=quest_data.domain,
        difficulty=quest_data.difficulty,
        xp_reward=quest_data.xp_reward,
        stat_rewards=quest_data.stat_rewards,
        estimated_duration=quest_data.estimated_duration,
        context_tags=quest_data.context_tags,
        ai_generated=quest_data.ai_generated,
        quest_date=today,
    )
    db.add(quest)
    await db.flush()
    await db.refresh(quest)
    return quest


async def complete_quest(
    quest_id: uuid.UUID, user: User, db: AsyncSession
) -> CompletionResult:
    quest = await db.get(Quest, quest_id)
    if not quest or quest.user_id != user.id:
        raise HTTPException(status_code=404, detail="Quest not found")
    if quest.is_completed:
        raise HTTPException(status_code=400, detail="Quest already completed")

    xp_gained = quest.xp_reward
    new_total_xp = user.total_xp + xp_gained

    new_stats = dict(user.stats) if user.stats else {}
    for stat, value in (quest.stat_rewards or {}).items():
        new_stats[stat.lower()] = min(100, new_stats.get(stat.lower(), 0) + value)

    new_rank = get_rank_from_xp(new_total_xp)
    new_level = get_level_from_xp(new_total_xp)
    leveled_up = new_level > user.level
    ranked_up = new_rank != user.rank

    streak_result = calculate_streak(user.last_active, user.current_streak, user.longest_streak)

    new_quests_by_domain = dict(user.quests_by_domain) if user.quests_by_domain else {}
    new_quests_by_domain[quest.domain.value] = (
        new_quests_by_domain.get(quest.domain.value, 0) + 1
    )

    new_achievements = await achievement_service.check_and_award(
        user_id=user.id,
        new_xp=new_total_xp,
        new_streak=streak_result["current_streak"],
        new_quest_count=user.total_quests_completed + 1,
        db=db,
    )

    quest.is_completed = True
    quest.completed_at = datetime.now(timezone.utc)
    user.total_xp = new_total_xp
    user.stats = new_stats
    user.rank = new_rank
    user.level = new_level
    user.current_streak = streak_result["current_streak"]
    user.longest_streak = streak_result["longest_streak"]
    user.total_quests_completed += 1
    user.quests_by_domain = new_quests_by_domain
    user.last_active = datetime.now(timezone.utc)

    await db.commit()

    from app.schemas.achievement import AchievementOut
    achievements_out = [AchievementOut.model_validate(a) for a in new_achievements]

    return CompletionResult(
        xp_gained=xp_gained,
        new_total_xp=new_total_xp,
        new_level=new_level,
        new_rank=new_rank,
        leveled_up=leveled_up,
        ranked_up=ranked_up,
        streak_info=streak_result,
        new_achievements=[a.model_dump() for a in achievements_out],
        updated_stats=quest.stat_rewards or {},
    )
