import asyncio
from datetime import date, timedelta, datetime, timezone
from app.celery_app import celery_app


@celery_app.task(name="tasks.notification_tasks.send_coach_message")
def send_coach_message(user_id: str, domain: str, quest_id: str):
    pass


@celery_app.task(name="tasks.notification_tasks.streak_check")
def streak_check():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def _run():
        from sqlalchemy import select
        from app.database import get_async_session
        from app.models.user import User

        async with get_async_session() as db:
            today = date.today()
            yesterday = today - timedelta(days=1)

            result = await db.execute(select(User))
            users = result.scalars().all()

            for user in users:
                if user.last_active is None:
                    continue
                last_date = user.last_active.date() if hasattr(user.last_active, "date") else user.last_active
                if isinstance(last_date, datetime):
                    last_date = last_date.date()
                delta = (today - last_date).days
                if delta > 1 and user.current_streak > 0:
                    user.current_streak = 0

            await db.commit()

    loop.run_until_complete(_run())
    loop.close()
