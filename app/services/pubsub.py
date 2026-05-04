import json
import logging
from typing import Any, Dict
import redis.asyncio as redis
from app.core.config import settings

logger = logging.getLogger(__name__)

# Single connection pool for async redis
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

async def publish_progress(task_id: str, user_id: str, payload: Dict[str, Any]):
    """
    Publish a progress update to a user-specific Redis channel.
    Channel format: `user_{user_id}_progress`
    """
    try:
        channel = f"user_{user_id}_progress"
        message = json.dumps({
            "task_id": task_id,
            **payload
        })
        await redis_client.publish(channel, message)
        logger.debug(f"Published to {channel}: {message}")
    except Exception as e:
        logger.error(f"Failed to publish progress to Redis: {e}")

async def get_subscriber(user_id: str):
    """
    Get a Redis PubSub object subscribed to the user's progress channel.
    """
    channel = f"user_{user_id}_progress"
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(channel)
    logger.info(f"Subscribed to {channel}")
    return pubsub

import redis as sync_redis

sync_redis_client = sync_redis.from_url(settings.REDIS_URL, decode_responses=True)

def sync_publish_progress(task_id: str, user_id: str, payload: Dict[str, Any]):
    """
    Publish a progress update synchronously (for use in Celery tasks).
    """
    try:
        channel = f"user_{user_id}_progress"
        message = json.dumps({
            "task_id": task_id,
            **payload
        })
        sync_redis_client.publish(channel, message)
        logger.debug(f"Sync published to {channel}: {message}")
    except Exception as e:
        logger.error(f"Failed to sync publish progress to Redis: {e}")
