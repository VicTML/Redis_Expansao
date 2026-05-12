import time
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
from .models import CacheRequest, TaskRequest
from .dependencies import cache, queue, rate_limiter

router = APIRouter()


# ==================== CACHE ====================

@router.get("/cache/{key}")
async def get_cache(key: str):
    """Recupera valor do cache"""
    value, is_hit = cache.get(key)
    return JSONResponse(
        {"key": key, "value": value, "cache_status": "HIT" if is_hit else "MISS"},
        headers={"X-Cache": "HIT" if is_hit else "MISS"}
    )


@router.post("/cache")
async def set_cache(data: CacheRequest):
    """Armazena valor no cache (TTL: 30s)"""
    success = cache.set(data.key, data.value)
    return {
        "success": success,
        "key": data.key,
        "ttl": 30,
        "message": "Armazenado" if success else "Erro"
    }


@router.get("/data")
async def data_endpoint():
    """Demo: primeira vez é lento (MISS), depois rápido (HIT)"""
    key = "computed_data"
    value, is_hit = cache.get(key)
    
    if is_hit:
        return JSONResponse(
            {
                "data": value,
                "from_cache": True,
                "latency_ms": 1
            },
            headers={"X-Cache": "HIT"}
        )
    
    # Simula computação
    start = time.time()
    time.sleep(0.2)
    data = {
        "result": 42,
        "timestamp": datetime.utcnow().isoformat()
    }
    latency = (time.time() - start) * 1000
    
    cache.set(key, data)
    
    return JSONResponse(
        {
            "data": data,
            "from_cache": False,
            "latency_ms": round(latency, 2)
        },
        headers={"X-Cache": "MISS"}
    )


# ==================== FILA ====================

@router.post("/job")
async def enqueue_job(task_name: str):
    """Enfileira uma tarefa"""
    task = {"id": int(time.time()), "action": task_name, "data": {}}
    success = queue.push(task)
    return {
        "success": success,
        "task": task,
        "queue_length": queue.length()
    }


@router.get("/jobs")
async def jobs_status():
    """Status da fila"""
    return {
        "pending_tasks": queue.length()
    }


# ==================== RATE LIMIT ====================

@router.get("/status")
async def status(request: Request):
    """Status da requisição (rate limit)"""
    ip = request.client.host
    count = rate_limiter.get_count(ip)
    remaining = max(0, rate_limiter.max_requests - count)
    
    return {
        "ip": ip,
        "requests_used": count,
        "requests_remaining": remaining,
        "limit": rate_limiter.max_requests,
        "window_seconds": rate_limiter.window
    }


# ==================== HEALTH ====================

@router.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Redis API",
        "endpoints": {
            "cache": "/cache/{key}",
            "data": "/data",
            "job": "/job",
            "jobs": "/jobs",
            "status": "/status",
            "docs": "/docs"
        }
    }


@router.get("/health")
async def health():
    """Health check"""
    from .dependencies import redis
    redis_ok = redis.ping()
    return {
        "status": "healthy" if redis_ok else "unhealthy",
        "redis": "connected" if redis_ok else "disconnected"
    }
