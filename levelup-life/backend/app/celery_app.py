from celery import Celery
from celery.schedules import crontab
from app.config import settings

celery_app = Celery(
    "levelup",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.quest_tasks",
        "app.tasks.analytics_tasks",
        "app.tasks.notification_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

celery_app.conf.beat_schedule = {
    "daily-snapshot": {
        "task": "tasks.analytics_tasks.daily_snapshot",
        "schedule": crontab(hour=0, minute=0),
    },
    "weekly-report": {
        "task": "tasks.analytics_tasks.weekly_report",
        "schedule": crontab(hour=8, minute=0, day_of_week=0),
    },
    "pre-generate-quests": {
        "task": "tasks.quest_tasks.pre_generate_quests",
        "schedule": crontab(hour=5, minute=0),
    },
    "streak-check": {
        "task": "tasks.notification_tasks.streak_check",
        "schedule": crontab(hour=23, minute=55),
    },
}
