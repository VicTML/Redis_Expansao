import json
import redis
from typing import Any, Optional
from datetime import datetime
from config import (
    REDIS_HOST, REDIS_PORT, REDIS_DB,
    CACHE_TTL, RATE_LIMIT_WINDOW, RATE_LIMIT_REQUESTS, QUEUE_NAME
)


class Redis:
    """Wrapper para operações Redis"""
    def __init__(self):
        self.client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True
        )

    def ping(self) -> bool:
        try:
            self.client.ping()
            return True
        except:
            return False


class Cache:
    """Gerenciador de Cache (SETEX/GET)"""
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    def get(self, key: str) -> tuple[Optional[Any], bool]:
        """Retorna (valor, is_hit)"""
        value = self.redis.get(key)
        if value:
            return json.loads(value), True
        return None, False

    def set(self, key: str, value: Any, ttl: int = CACHE_TTL) -> bool:
        try:
            serialized = json.dumps(value) if isinstance(value, (dict, list)) else str(value)
            self.redis.setex(key, ttl, serialized)
            return True
        except:
            return False


class Queue:
    """Gerenciador de Fila (LPUSH/BRPOP)"""
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.name = QUEUE_NAME

    def push(self, task: dict) -> bool:
        try:
            task["timestamp"] = datetime.utcnow().isoformat()
            self.redis.lpush(self.name, json.dumps(task))
            return True
        except:
            return False

    def pop_blocking(self, timeout: int = 0) -> Optional[dict]:
        try:
            result = self.redis.brpop(self.name, timeout)
            return json.loads(result[1]) if result else None
        except:
            return None

    def length(self) -> int:
        return self.redis.llen(self.name)


class RateLimiter:
    """Rate Limiter por IP (INCR/EXPIRE)"""
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.window = RATE_LIMIT_WINDOW
        self.max_requests = RATE_LIMIT_REQUESTS

    def is_allowed(self, ip: str) -> tuple[bool, int]:
        """Retorna (permitido, restantes)"""
        key = f"rate_limit:{ip}"
        try:
            current = self.redis.incr(key)
            if current == 1:
                self.redis.expire(key, self.window)
            remaining = max(0, self.max_requests - current)
            return current <= self.max_requests, remaining
        except:
            return True, self.max_requests

    def get_count(self, ip: str) -> int:
        key = f"rate_limit:{ip}"
        count = self.redis.get(key)
        return int(count) if count else 0


# Instâncias globais
redis_wrapper = Redis()
cache = Cache(redis_wrapper.client)
queue = Queue(redis_wrapper.client)
rate_limiter = RateLimiter(redis_wrapper.client)