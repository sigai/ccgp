import redis
# 建立redis连接
default_redis_uri = "redis://:root@127.0.0.1:6379/0"
connection_pool = redis.BlockingConnectionPool.from_url(
    default_redis_uri, max_connections=10, timeout=60
)
redis_conn = redis.StrictRedis(connection_pool=connection_pool)
redis_conn.set('qq','qwww')
qq=redis_conn.get('qq')
print(qq)
