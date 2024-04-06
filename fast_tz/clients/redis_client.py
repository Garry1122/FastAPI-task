import logging

import redis
from redis import ConnectionPool, StrictRedis

logger = logging.getLogger(__name__)


class RedisClient(object):
    def __init__(self, host, port, db):
        pool = ConnectionPool(
            host=host,
            port=port,
            db=db,
        )
        self.instance = StrictRedis(connection_pool=pool)

    def set(self, key: str, value: str, timeout=60):
        try:
            if key is not None and value is not None:
                self.instance.set(name=key, value=value, ex=timeout)
        except Exception as e:
            logger.exception(f"Could not set data to redis db, key: {key}")
            return None

    def get(self, key: str):
        try:
            if key is not None and self.instance.exists(key):
                cached_data = self.instance.get(key).decode("utf-8")
                return cached_data
        except Exception as e:
            logger.error("Could not get data from redis db")
            return None

    def scan(self, pattern: str):
        try:
            keys = []
            cursor = "0"
            while cursor != 0:
                cursor, results = self.instance.scan(cursor=cursor, match=pattern)
                keys.extend(results)
            return keys
        except Exception as e:
            logger.exception("Could not scan Redis keys")
            return None

    def delete(self, key: str):
        try:
            if key is not None and self.instance.exists(key):
                self.instance.delete(key)
        except Exception as e:
            logger.exception(f"Could not delete key from Redis DB, key: {key}")

    def is_online(self):
        try:
            self.instance.ping()
            return True
        except ConnectionError:
            return False
