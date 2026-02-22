import uuid
from datetime import datetime, timezone, date
from sqlalchemy import Integer, Text, TIMESTAMP, Date, ForeignKey, UniqueConstraint, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class AnalyticsSnapshot(Base):
    __tablename__ = "analytics_snapshots"
    __table_args__ = (
        UniqueConstraint("user_id", "snapshot_date", name="uq_user_snapshot_date"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False)
    quests_completed: Mapped[int] = mapped_column(Integer, default=0)
    xp_earned: Mapped[int] = mapped_column(Integer, default=0)
    domain_breakdown: Mapped[dict] = mapped_column(JSON, default=dict)
    streak_at_snapshot: Mapped[int] = mapped_column(Integer, nullable=False)
    ai_insights: Mapped[str | None] = mapped_column(Text, nullable=True)
    stats_snapshot: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship("User", back_populates="analytics_snapshots")
