import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from src.api.dependencies import cache, queue, rate_limiter


client = TestClient(app)


@pytest.fixture(autouse=True)
def cleanup():
    """Limpa dados antes e depois de cada teste"""
    cache.redis.flushdb()
    queue.redis.delete(queue.name)
    yield
    cache.redis.flushdb()
    queue.redis.delete(queue.name)


# Cache
def test_cache_set_get():
    response = client.post("/cache", json={"key": "test", "value": "data"})
    assert response.status_code == 200
    
    response = client.get("/cache/test")
    assert response.json()["cache_status"] == "HIT"


def test_cache_miss():
    response = client.get("/cache/missing")
    assert response.headers["X-Cache"] == "MISS"


def test_data_endpoint():
    r1 = client.get("/data")
    assert r1.headers["X-Cache"] == "MISS"
    
    r2 = client.get("/data")
    assert r2.headers["X-Cache"] == "HIT"


# Queue
def test_job_enqueue():
    response = client.post("/job?task_name=GerarRelatorio")
    assert response.status_code == 200
    assert response.json()["queue_length"] == 1


def test_jobs_status():
    client.post("/job?task_name=Test1")
    client.post("/job?task_name=Test2")
    
    response = client.get("/jobs")
    assert response.json()["pending_tasks"] == 2


# Health
def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "endpoints" in response.json()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
