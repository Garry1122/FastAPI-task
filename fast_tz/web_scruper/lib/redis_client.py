import redis
from django.conf import settings


class RedisOperation(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            pool = redis.ConnectionPool(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_RESULT_DB,
                connection_class=redis.SSLConnection,
                ssl_cert_reqs=None
            )
            cls.instance = redis.StrictRedis(connection_pool=pool)
        return cls.instance
