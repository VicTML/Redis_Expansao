from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from datetime import datetime
from .routes import router
from .dependencies import rate_limiter

app = FastAPI(
    title="Redis API",
    description="Cache, Fila e Rate Limiting",
    version="1.0.0"
)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Middleware de rate limiting por IP"""
    ip = request.client.host
    allowed, remaining = rate_limiter.is_allowed(ip)
    
    if not allowed:
        return JSONResponse(
            {"error": "Too many requests", "ip": ip},
            status_code=429,
            headers={"X-RateLimit-Remaining": "0"}
        )
    
    response = await call_next(request)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Limit"] = str(rate_limiter.max_requests)
    return response


app.include_router(router)


@app.on_event("startup")
async def startup():
    from .dependencies import redis
    if redis.ping():
        print("✓ Conectado ao Redis")
    else:
        print("✗ Falha ao conectar ao Redis")
