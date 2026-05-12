import redis

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

pool = redis.ConnectionPool(host='localhost', port=6379, db=0, decode_responses=True)
r = redis.Redis(connection_pool=pool)

r.ping()