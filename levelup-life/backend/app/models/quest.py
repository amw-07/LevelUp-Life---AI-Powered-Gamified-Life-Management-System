import uuid
from datetime import datetime, timezone, date
from sqlalchemy import String, Integer, Boolean, Text, TIMESTAMP, Date, Enum as SAEnum, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import enum


class QuestDomain(str, enum.Enum):
    fitness = "fitness"
    productivity = "productivity"
    learning = "learning"


class QuestDifficulty(str, enum.Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class Quest(Base):
    __tablename__ = "quests"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    domain: Mapped[QuestDomain] = mapped_column(
        SAEnum(QuestDomain, name="quest_domain"), nullable=False
    )
    difficulty: Mapped[QuestDifficulty] = mapped_column(
        SAEnum(QuestDifficulty, name="difficulty"), nullable=False
    )
    xp_reward: Mapped[int] = mapped_column(Integer, nullable=False)
    stat_rewards: Mapped[dict] = mapped_column(JSON, default=dict)
    estimated_duration: Mapped[str] = mapped_column(String(30), nullable=True)
    context_tags: Mapped[list] = mapped_column(JSON, default=list)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    completed_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    quest_date: Mapped[date] = mapped_column(Date, nullable=False)
    ai_generated: Mapped[bool] = mapped_column(Boolean, default=True)
    agent_context: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship("User", back_populates="quests")
