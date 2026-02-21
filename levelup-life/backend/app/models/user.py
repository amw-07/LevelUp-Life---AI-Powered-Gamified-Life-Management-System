import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Boolean, Text, TIMESTAMP, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import event
from app.database import Base


def _jsonb_or_json():
    try:
        from sqlalchemy.dialects.postgresql import JSONB as _JSONB
        return _JSONB
    except Exception:
        return JSON


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(Text, nullable=False)
    level: Mapped[int] = mapped_column(Integer, default=1)
    total_xp: Mapped[int] = mapped_column(Integer, default=0)
    rank: Mapped[str] = mapped_column(String(2), default="E")
    current_streak: Mapped[int] = mapped_column(Integer, default=0)
    longest_streak: Mapped[int] = mapped_column(Integer, default=0)
    stats: Mapped[dict] = mapped_column(JSON, default=dict)
    goals: Mapped[dict] = mapped_column(JSON, default=dict)
    mindset_profile: Mapped[list] = mapped_column(JSON, default=list)
    work_style: Mapped[str] = mapped_column(String(30), default="balanced")
    activity_level: Mapped[str] = mapped_column(String(20), default="intermediate")
    preferred_times: Mapped[dict] = mapped_column(JSON, default=dict)
    quests_by_domain: Mapped[dict] = mapped_column(JSON, default=dict)
    total_quests_completed: Mapped[int] = mapped_column(Integer, default=0)
    last_active: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    onboarding_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    quests: Mapped[list["Quest"]] = relationship(
        "Quest", back_populates="user", cascade="all, delete-orphan"
    )
    achievements: Mapped[list["Achievement"]] = relationship(
        "Achievement", back_populates="user", cascade="all, delete-orphan"
    )
    analytics_snapshots: Mapped[list["AnalyticsSnapshot"]] = relationship(
        "AnalyticsSnapshot", back_populates="user", cascade="all, delete-orphan"
    )
