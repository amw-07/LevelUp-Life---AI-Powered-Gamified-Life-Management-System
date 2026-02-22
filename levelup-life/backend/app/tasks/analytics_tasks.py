import uuid
import asyncio
from datetime import date, timedelta, datetime
from sqlalchemy import select, func
from app.celery_app import celery_app
from app.database import get_async_session
from app.models.user import User
from app.models.quest import Quest
from app.models.analytics import AnalyticsSnapshot
from app.services.analytics_service import get_weekly_report
from app.agents.crews import create_analytics_crew
from sqlalchemy.ext.asyncio import AsyncSession


@celery_app.task(name="tasks.analytics_tasks.daily_snapshot")
def daily_snapshot():
    """Create daily analytics snapshot for all users at 00:00 UTC."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def run_snapshot():
        async with get_async_session() as db:
            today = date.today()

            # Get all users
            result = await db.execute(select(User))
            users = result.scalars().all()

            for user in users:
                # Calculate daily metrics
                yesterday = today - timedelta(days=1)

                quests_result = await db.execute(
                    select(
                        func.count(Quest.id).label("total"),
                        func.sum(Quest.xp_reward).label("xp"),
                        Quest.domain,
                    ).where(
                        Quest.user_id == user.id,
                        Quest.is_completed == True,
                        Quest.quest_date == yesterday,
                    ).group_by(Quest.domain)
                )

                rows = quests_result.all()
                domain_breakdown = {}
                total_completed = 0
                total_xp = 0

                for row in rows:
                    domain_breakdown[row.domain.value] = {
                        "completed": row.total or 0,
                        "xp": int(row.xp or 0),
                    }
                    total_completed += row.total or 0
                    total_xp += row.xp or 0

                # Check if snapshot already exists
                existing_result = await db.execute(
                    select(AnalyticsSnapshot).where(
                        AnalyticsSnapshot.user_id == user.id,
                        AnalyticsSnapshot.snapshot_date == yesterday,
                    )
                )
                existing = existing_result.scalar_one_or_none()

                if existing:
                    existing.quests_completed = total_completed
                    existing.xp_earned = total_xp
                    existing.domain_breakdown = domain_breakdown
                    existing.streak_at_snapshot = user.current_streak
                    existing.stats_snapshot = user.stats
                else:
                    snapshot = AnalyticsSnapshot(
                        user_id=user.id,
                        snapshot_date=yesterday,
                        quests_completed=total_completed,
                        xp_earned=total_xp,
                        domain_breakdown=domain_breakdown,
                        streak_at_snapshot=user.current_streak,
                        stats_snapshot=user.stats,
                    )
                    db.add(snapshot)

            await db.commit()

    loop.run_until_complete(run_snapshot())
    loop.close()


@celery_app.task(name="tasks.analytics_tasks.weekly_report")
def weekly_report():
    """Generate AI-powered weekly report insights on Sunday 08:00 UTC."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def run_report():
        async with get_async_session() as db:
            today = date.today()
            week_start = today - timedelta(days=today.weekday())
            last_week_start = week_start - timedelta(days=7)

            # Get all users
            result = await db.execute(select(User))
            users = result.scalars().all()

            for user in users:
                # Get weekly data
                week_data = await get_weekly_report(user.id, last_week_start.strftime("%Y-%W"), db)

                # Skip if no activity
                if week_data["metrics"]["total"]["completed"] == 0:
                    continue

                # Generate AI insights using Analytics crew
                try:
                    crew = create_analytics_crew(user, week_data)
                    insights_result = crew.kickoff()

                    # Get AI-generated insights
                    insights_text = str(insights_result)

                    # Update snapshot with AI insights
                    snapshot_result = await db.execute(
                        select(AnalyticsSnapshot).where(
                            AnalyticsSnapshot.user_id == user.id,
                            AnalyticsSnapshot.snapshot_date == last_week_start,
                        )
                    )
                    snapshot = snapshot_result.scalar_one_or_none()

                    if snapshot:
                        snapshot.ai_insights = insights_text
                    else:
                        # Create snapshot if it doesn't exist
                        snapshot = AnalyticsSnapshot(
                            user_id=user.id,
                            snapshot_date=last_week_start,
                            quests_completed=week_data["metrics"]["total"]["completed"],
                            xp_earned=week_data["metrics"]["total"]["xp"],
                            domain_breakdown={k: v for k, v in week_data["metrics"].items() if k != "total"},
                            streak_at_snapshot=user.current_streak,
                            ai_insights=insights_text,
                            stats_snapshot=user.stats,
                        )
                        db.add(snapshot)

                    await db.commit()
                except Exception as e:
                    print(f"Error generating weekly report for user {user.id}: {e}")
                    continue

    loop.run_until_complete(run_report())
    loop.close()


@celery_app.task(name="tasks.analytics_tasks.generate_coach_message")
def generate_coach_message(user_id: str):
    """Generate personalized coaching message using Personalized Coach agent."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def run_message_generation():
        async with get_async_session() as db:
            from app.agents.crews import create_coach_crew

            # Get user
            result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
            user = result.scalar_one_or_none()

            if not user:
                return

            try:
                # Generate coaching message
                crew = create_coach_crew(user)
                message = crew.kickoff()

                # Store message (you might want to add a notifications table)
                # For now, we'll just return it
                return str(message)
            except Exception as e:
                print(f"Error generating coach message for user {user.id}: {e}")
                return None

    result = loop.run_until_complete(run_message_generation())
    loop.close()
    return result
