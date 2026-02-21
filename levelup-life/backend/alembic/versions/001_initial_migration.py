"""Initial migration

Revision ID: 001
Revises:
Create Date: 2025-01-01 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

    op.execute("CREATE TYPE quest_domain AS ENUM ('fitness', 'productivity', 'learning')")
    op.execute("CREATE TYPE difficulty AS ENUM ('easy', 'medium', 'hard')")

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("username", sa.String(50), unique=True, nullable=False),
        sa.Column("hashed_password", sa.Text, nullable=False),
        sa.Column("level", sa.Integer, default=1, server_default="1"),
        sa.Column("total_xp", sa.Integer, default=0, server_default="0"),
        sa.Column("rank", sa.String(2), default="E", server_default="E"),
        sa.Column("current_streak", sa.Integer, default=0, server_default="0"),
        sa.Column("longest_streak", sa.Integer, default=0, server_default="0"),
        sa.Column("stats", postgresql.JSONB, server_default="{}"),
        sa.Column("goals", postgresql.JSONB, server_default="{}"),
        sa.Column("mindset_profile", postgresql.ARRAY(sa.Text), server_default="{}"),
        sa.Column("work_style", sa.String(30), default="balanced", server_default="balanced"),
        sa.Column("activity_level", sa.String(20), default="intermediate", server_default="intermediate"),
        sa.Column("preferred_times", postgresql.JSONB, server_default="{}"),
        sa.Column("quests_by_domain", postgresql.JSONB, server_default="{}"),
        sa.Column("total_quests_completed", sa.Integer, default=0, server_default="0"),
        sa.Column("last_active", sa.TIMESTAMP(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("onboarding_completed", sa.Boolean, default=False, server_default="FALSE"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "quests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("domain", sa.Enum("fitness", "productivity", "learning", name="quest_domain", create_type=False), nullable=False),
        sa.Column("difficulty", sa.Enum("easy", "medium", "hard", name="difficulty", create_type=False), nullable=False),
        sa.Column("xp_reward", sa.Integer, nullable=False),
        sa.Column("stat_rewards", postgresql.JSONB, server_default="{}"),
        sa.Column("estimated_duration", sa.String(30), nullable=True),
        sa.Column("context_tags", postgresql.ARRAY(sa.Text), server_default="{}"),
        sa.Column("is_completed", sa.Boolean, default=False, server_default="FALSE"),
        sa.Column("completed_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("quest_date", sa.Date, nullable=False),
        sa.Column("ai_generated", sa.Boolean, default=True, server_default="TRUE"),
        sa.Column("agent_context", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("ix_quests_user_date", "quests", ["user_id", "quest_date"])
    op.create_index("ix_quests_user_completed", "quests", ["user_id", "is_completed"])

    op.create_table(
        "achievements",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("key", sa.String(50), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("icon", sa.String(10), nullable=False),
        sa.Column("earned_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("NOW()")),
        sa.UniqueConstraint("user_id", "key", name="uq_user_achievement_key"),
    )

    op.create_table(
        "analytics_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("snapshot_date", sa.Date, nullable=False),
        sa.Column("quests_completed", sa.Integer, default=0, server_default="0"),
        sa.Column("xp_earned", sa.Integer, default=0, server_default="0"),
        sa.Column("domain_breakdown", postgresql.JSONB, server_default="{}"),
        sa.Column("streak_at_snapshot", sa.Integer, nullable=False),
        sa.Column("ai_insights", sa.Text, nullable=True),
        sa.Column("stats_snapshot", postgresql.JSONB, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("NOW()")),
        sa.UniqueConstraint("user_id", "snapshot_date", name="uq_user_snapshot_date"),
    )


def downgrade() -> None:
    op.drop_table("analytics_snapshots")
    op.drop_table("achievements")
    op.drop_table("quests")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS quest_domain")
    op.execute("DROP TYPE IF EXISTS difficulty")
