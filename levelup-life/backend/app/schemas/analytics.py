import uuid
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel


class AnalyticsSnapshotOut(BaseModel):
    id: uuid.UUID
    snapshot_date: date
    quests_completed: int
    xp_earned: int
    domain_breakdown: dict
    streak_at_snapshot: int
    ai_insights: Optional[str]
    stats_snapshot: dict

    class Config:
        from_attributes = True


class SummaryOut(BaseModel):
    this_week: dict
    all_time: dict
    domain_distribution: dict


class StreakDataPoint(BaseModel):
    date: str
    completed_count: int


class PatternsOut(BaseModel):
    best_day: Optional[str]
    best_time: Optional[str]
    top_domain: Optional[str]
    completion_rate_trend: Optional[float]
