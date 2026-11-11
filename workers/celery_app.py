from celery import Celery

from backend.app.config import get_settings

settings = get_settings()
celery_app = Celery(
    "knowbridge",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["workers.tasks"],
)
celery_app.conf.update(
    accept_content=["json"],
    result_accept_content=["json"],
    task_serializer="json",
    result_serializer="json",
    task_track_started=True,
    result_expires=3600,
)
