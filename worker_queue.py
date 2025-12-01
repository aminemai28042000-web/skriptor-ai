import redis.asyncio as redis
import json
from config import REDIS_URL

redis_client = redis.from_url(REDIS_URL)

QUEUE_NAME = "tasks_queue"


async def enqueue_task(task: dict):
    """
    Добавляет задачу в Redis очередь.
    """
    await redis_client.lpush(QUEUE_NAME, json.dumps(task))


async def dequeue_task():
    """
    Рабочий тянет задачу из Redis очереди.
    """
    item = await redis_client.rpop(QUEUE_NAME)
    if item:
        return json.loads(item)
    return None
