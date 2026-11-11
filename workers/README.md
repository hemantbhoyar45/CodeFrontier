# KNOWBRIDGE worker

The worker is a separate Celery process that shares the backend settings and
dependency environment. Start it from the repository root after configuring
`.env` and starting Redis:

```powershell
python -m celery -A workers.celery_app:celery_app worker --loglevel=INFO
```

The `knowbridge.sample.add` task is a deterministic smoke-test task; it is not
a substitute for product processing jobs.
