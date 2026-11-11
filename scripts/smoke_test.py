"""Verify the running web/API stack and a real Celery task round trip."""

import os
import sys
from urllib.error import URLError
from urllib.request import urlopen

from workers.celery_app import celery_app

FRONTEND_URL = os.getenv("SMOKE_FRONTEND_URL", "http://localhost:3000")
API_READY_URL = os.getenv(
    "SMOKE_API_READY_URL",
    "http://localhost:8000/api/v1/health/ready",
)


def check_http(url: str, expected_content: bytes | None = None) -> None:
    try:
        with urlopen(url, timeout=5) as response:
            body = response.read()
            if response.status != 200:
                raise RuntimeError(f"{url} returned HTTP {response.status}")
            if expected_content is not None and expected_content not in body:
                raise RuntimeError(f"{url} did not contain expected content")
    except URLError as exc:
        raise RuntimeError(f"Could not reach {url}: {exc}") from exc


def main() -> int:
    check_http(FRONTEND_URL, b"KNOWBRIDGE")
    check_http(API_READY_URL, b'"database":"ok"')

    result = celery_app.send_task("knowbridge.sample.add", args=[19, 23])
    value = result.get(timeout=20, propagate=True)
    if value != 42:
        raise RuntimeError(f"Celery smoke task returned {value!r}, expected 42")

    print("Smoke checks passed: frontend, API/database readiness, and Celery task.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Smoke check failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
