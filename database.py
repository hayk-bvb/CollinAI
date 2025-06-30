from langgraph.checkpoint.redis import RedisSaver
import redis
import logging

logger = logging.getLogger(__name__)

class RedisClient:
    """A class to represent the database used for memory for the RAG application. Hosted with Redis"""

    def __init__(self, url="redis://localhost:6379", cold_start:bool=False):
            try:
                self.client = redis.Redis.from_url(url)
                # Test the connection
                self.client.ping()
                logger.info("Connected to Redis server successfully.")
            except redis.ConnectionError as e:
                logger.error(f"Failed to connect to Redis server: {e}")
                self.client = None

            finally:
                with RedisSaver.from_conn_string(url) as checkpointer:
                    if cold_start:
                        checkpointer.setup()
                    self._checkpointer = checkpointer

    def get_checkpointer(self):
        """Returns the checkpointer instance. """
        return self._checkpointer

    def set(self, key, value):
        if self.client:
            self.client.set(key, value)

    def get(self, key):
        if self.client:
            return self.client.get(key)
        
    # TODO: Need to make method to wipe the database


if __name__ == "__main__":
    redis_client = RedisClient()
    # print(redis_client.get_checkpointer())
    # redis_client.set("test_key", "hello")
    # print(redis_client.get("test_key"))  # Output: b'hello'




