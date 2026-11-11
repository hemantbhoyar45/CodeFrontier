from redis import Redis

from backend.app.config import get_settings

settings = get_settings()
redis_client = Redis.from_url(
    settings.redis_url,
    decode_responses=True,
    socket_connect_timeout=1,
    socket_timeout=1,
)
