import uuid
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel
from app.models.quest import QuestDomain, QuestDifficulty


class QuestCreate(BaseModel):
    title: str
    description: str
    domain: QuestDomain
    difficulty: QuestDifficulty
    xp_reward: int
    stat_rewards: dict = {}
    estimated_duration: Optional[str] = None
    context_tags: List[str] = []
    ai_generated: bool = False


class QuestOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    description: str
    domain: QuestDomain
    difficulty: QuestDifficulty
    xp_reward: int
    stat_rewards: dict
    estimated_duration: Optional[str]
    context_tags: list
    is_completed: bool
    completed_at: Optional[datetime]
    quest_date: date
    ai_generated: bool
    created_at: datetime

    class Config:
        from_attributes = True


class CompletionResult(BaseModel):
    xp_gained: int
    new_total_xp: int
    new_level: int
    new_rank: str
    leveled_up: bool
    ranked_up: bool
    streak_info: dict
    new_achievements: list
    updated_stats: dict
