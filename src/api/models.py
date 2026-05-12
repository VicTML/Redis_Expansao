from pydantic import BaseModel
from typing import Any, Optional


class CacheRequest(BaseModel):
    key: str
    value: Any


class TaskRequest(BaseModel):
    id: int
    action: str
    data: dict


class RateLimitInfo(BaseModel):
    ip: str
    requests_used: int
    requests_remaining: int
    limit_per_window: int
    window_seconds: int
