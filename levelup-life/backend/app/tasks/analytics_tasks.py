from app.celery_app import celery_app


@celery_app.task(name="tasks.analytics_tasks.daily_snapshot")
def daily_snapshot():
    pass


@celery_app.task(name="tasks.analytics_tasks.weekly_report")
def weekly_report():
    pass
