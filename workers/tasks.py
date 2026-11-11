from workers.celery_app import celery_app


@celery_app.task(name="knowbridge.sample.add")
def add(left: int, right: int) -> int:
    """Small deterministic task to verify worker dispatch and execution."""
    return left + right
