import uuid
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.database import get_db
from app.models.user import User
from app.models.quest import Quest
from app.schemas.quest import QuestCreate, QuestOut, CompletionResult
from app.services.user_service import get_current_user
from app.services.quest_service import get_quests_for_today, create_quest, complete_quest
from app.redis_client import get_redis
import redis.asyncio as aioredis

router = APIRouter()

QUESTS_TODAY_TTL = 60


@router.get("/today")
async def get_today_quests(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    quests = await get_quests_for_today(user.id, db)
    generating = False
    task_id = None

    if not quests:
        generating = True
        rate_key = f"quest_gen:{user.id}:{date.today()}"
        count = await redis.get(rate_key)
        if not count or int(count) < 3:
            try:
                from app.celery_app import celery_app
                task = celery_app.send_task(
                    "tasks.generate_quests", args=[str(user.id)]
                )
                task_id = task.id
                await redis.incr(rate_key)
                await redis.expire(rate_key, 86400)
            except Exception:
                generating = False

    return {
        "quests": [QuestOut.model_validate(q) for q in quests],
        "generating": generating,
        "task_id": task_id,
    }


@router.post("/generate")
async def force_generate(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    rate_key = f"quest_gen:{user.id}:{date.today()}"
    count = await redis.get(rate_key)
    if count and int(count) >= 3:
        raise HTTPException(status_code=429, detail="Quest generation limit reached (3/day)")

    from app.celery_app import celery_app
    task = celery_app.send_task("tasks.generate_quests", args=[str(user.id)])
    await redis.incr(rate_key)
    await redis.expire(rate_key, 86400)

    return {"task_id": task.id}


@router.post("/{quest_id}/complete", response_model=CompletionResult)
async def complete(
    quest_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await complete_quest(quest_id, user, db)


@router.get("/history")
async def get_history(
    days: int = 30,
    domain: Optional[str] = None,
    limit: int = 50,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from datetime import timedelta
    start_date = date.today() - timedelta(days=days)
    conditions = [Quest.user_id == user.id, Quest.quest_date >= start_date]
    if domain:
        from app.models.quest import QuestDomain
        conditions.append(Quest.domain == QuestDomain(domain))

    result = await db.execute(
        select(Quest).where(and_(*conditions)).order_by(Quest.created_at.desc()).limit(limit)
    )
    quests = result.scalars().all()
    return [QuestOut.model_validate(q) for q in quests]


@router.post("/", response_model=QuestOut, status_code=201)
async def create_manual_quest(
    body: QuestCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    body.ai_generated = False
    quest = await create_quest(user.id, body, db)
    return QuestOut.model_validate(quest)


@router.delete("/{quest_id}", status_code=204)
async def delete_quest(
    quest_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    quest = await db.get(Quest, quest_id)
    if not quest or quest.user_id != user.id:
        raise HTTPException(status_code=404, detail="Quest not found")
    if quest.is_completed:
        raise HTTPException(status_code=400, detail="Cannot delete completed quest")
    await db.delete(quest)
