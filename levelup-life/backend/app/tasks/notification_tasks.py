from app.celery_app import celery_app


@celery_app.task(name="tasks.notification_tasks.generate_coach_message")
def generate_coach_message(user_id: str, domain: str, quest_id: str):
    pass


@celery_app.task(name="tasks.notification_tasks.streak_check")
def streak_check():
    pass
