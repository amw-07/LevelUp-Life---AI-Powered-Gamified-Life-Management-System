import asyncio
from app.celery_app import celery_app


@celery_app.task(bind=True, max_retries=3, default_retry_delay=10, name="tasks.generate_quests")
def generate_quests_task(self, user_id: str):
    try:
        result = asyncio.run(_generate_quests_async(user_id))
        return result
    except Exception as exc:
        raise self.retry(exc=exc)


async def _generate_quests_async(user_id: str) -> dict:
    import uuid
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
    from app.config import settings
    from app.services.user_service import get_user_by_id
    from app.services.quest_service import create_quest, get_quests_for_today
    from app.agents.crews import create_daily_quest_crew
    from app.agents.parsers import parse_quest_list

    engine = create_async_engine(settings.DATABASE_URL)
    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    try:
        async with session_factory() as db:
            user = await get_user_by_id(uuid.UUID(user_id), db)
            if not user:
                return {"status": "error", "detail": "User not found"}

            existing = await get_quests_for_today(user.id, db)
            if existing:
                return {"status": "skipped", "count": len(existing)}

            crew = create_daily_quest_crew(user)
            raw_result = crew.kickoff()

            raw_text = str(raw_result)
            quests_data = parse_quest_list(raw_text)

            created = []
            for quest_data in quests_data:
                quest = await create_quest(user.id, quest_data, db)
                created.append(quest)

            await db.commit()
            return {"status": "ok", "count": len(created)}
    finally:
        await engine.dispose()


@celery_app.task(name="tasks.quest_tasks.pre_generate_quests")
def pre_generate_quests():
    import asyncio

    async def _run():
        from sqlalchemy import select
        from app.database import get_async_session
        from app.models.user import User

        async with get_async_session() as db:
            result = await db.execute(select(User).where(User.onboarding_completed == True))
            users = result.scalars().all()
            for user in users:
                celery_app.send_task("tasks.generate_quests", args=[str(user.id)])

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_run())
    loop.close()
