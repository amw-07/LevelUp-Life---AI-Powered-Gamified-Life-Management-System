from app.celery_app import celery_app


@celery_app.task(bind=True, max_retries=3, default_retry_delay=10, name="tasks.generate_quests")
def generate_quests_task(self, user_id: str):
    try:
        return {"status": "ok", "count": 0, "note": "AI agents not yet configured"}
    except Exception as exc:
        raise self.retry(exc=exc)


@celery_app.task(name="tasks.quest_tasks.pre_generate_quests")
def pre_generate_quests():
    pass
