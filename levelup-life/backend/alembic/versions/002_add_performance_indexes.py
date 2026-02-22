"""Add performance indexes

Revision ID: 002
Revises: 001
Create Date: 2025-01-02 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_users_email_perf ON users (email)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_quests_user_date_perf ON quests (user_id, quest_date)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_quests_user_completed_perf ON quests (user_id, is_completed)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_users_email_perf")
    op.execute("DROP INDEX IF EXISTS ix_quests_user_date_perf")
    op.execute("DROP INDEX IF EXISTS ix_quests_user_completed_perf")
