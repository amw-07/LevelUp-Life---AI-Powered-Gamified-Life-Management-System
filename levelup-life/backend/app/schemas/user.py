import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr
from app.schemas.achievement import AchievementOut


class UserStats(BaseModel):
    strength: int = 0
    vitality: int = 0
    endurance: int = 0
    focus: int = 0
    efficiency: int = 0
    execution: int = 0
    intelligence: int = 0
    creativity: int = 0
    wisdom: int = 0


class UserOut(BaseModel):
    id: uuid.UUID
    email: str
    username: str
    level: int
    total_xp: int
    rank: str
    current_streak: int
    longest_streak: int
    stats: dict
    goals: dict
    mindset_profile: list
    work_style: str
    activity_level: str
    quests_by_domain: dict
    total_quests_completed: int
    onboarding_completed: bool
    achievements: List[AchievementOut] = []
    created_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def model_validate(cls, obj, **kwargs):
        try:
            achievements = list(obj.achievements) if hasattr(obj, 'achievements') else []
        except Exception:
            achievements = []
        data = {
            "id": obj.id,
            "email": obj.email,
            "username": obj.username,
            "level": obj.level,
            "total_xp": obj.total_xp,
            "rank": obj.rank,
            "current_streak": obj.current_streak,
            "longest_streak": obj.longest_streak,
            "stats": obj.stats or {},
            "goals": obj.goals or {},
            "mindset_profile": obj.mindset_profile or [],
            "work_style": obj.work_style,
            "activity_level": obj.activity_level,
            "quests_by_domain": obj.quests_by_domain or {},
            "total_quests_completed": obj.total_quests_completed,
            "onboarding_completed": obj.onboarding_completed,
            "achievements": [AchievementOut.model_validate(a) for a in achievements],
            "created_at": obj.created_at,
        }
        return cls(**data)


class UserUpdate(BaseModel):
    username: Optional[str] = None
    work_style: Optional[str] = None
    activity_level: Optional[str] = None
    goals: Optional[dict] = None
    mindset_profile: Optional[List[str]] = None
    preferred_times: Optional[dict] = None


class OnboardingRequest(BaseModel):
    goals: dict
    mindset_profile: List[str]
    work_style: str
    activity_level: str
    preferred_times: dict


class UserStatsOut(BaseModel):
    level: int
    total_xp: int
    rank: str
    current_streak: int
    longest_streak: int
    stats: dict
    quests_by_domain: dict

    class Config:
        from_attributes = True
