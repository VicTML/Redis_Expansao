import os
from dotenv import load_dotenv

load_dotenv()

# Redis
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# Cache
CACHE_TTL = 30

# Rate Limit
RATE_LIMIT_WINDOW = 60
RATE_LIMIT_REQUESTS = 5

# Queue
QUEUE_NAME = "job_queue"
