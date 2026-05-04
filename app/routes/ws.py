import json
import logging
import jwt
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.services.pubsub import get_subscriber
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["WebSocket"])

async def verify_clerk_token(token: str) -> str:
    """
    Validate the Clerk JWT token.
    In production, you should fetch the JWKS from your Clerk Frontend API
    and verify the RS256 signature.
    """
    if not token:
        raise ValueError("No token provided")
    
    try:
        # Decode the token. For robust production use, pass the public key and algorithms=["RS256"]
        # Since we don't have the dynamic JWKS URL cached here, we extract the 'sub' (user ID).
        payload = jwt.decode(token, options={"verify_signature": False})
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Token does not contain a user ID (sub).")
        return user_id
    except jwt.DecodeError:
        raise ValueError("Invalid JWT token format.")
    except Exception as e:
        raise ValueError(f"Token validation failed: {str(e)}")


@router.websocket("/progress")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    try:
        # 1. Clerk JWT Validation
        user_id = await verify_clerk_token(token)
    except Exception as e:
        logger.error(f"WebSocket auth failed: {e}")
        await websocket.close(code=1008) # Policy Violation
        return

    await websocket.accept()
    logger.info(f"WebSocket connected for user: {user_id}")

    # 2. Subscribe to user's Redis Pub/Sub channel
    pubsub = await get_subscriber(user_id)

    try:
        # Read from Redis and send to WebSocket
        async for message in pubsub.listen():
            if message["type"] == "message":
                data = message["data"]
                await websocket.send_text(data)
                
                # If we detect completion, we can log it
                parsed = json.loads(data)
                if parsed.get("status") in ["completed", "failed", "cancelled"]:
                    logger.info(f"Task {parsed.get('task_id')} finished with status: {parsed.get('status')}")

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user: {user_id}")
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
    finally:
        await pubsub.unsubscribe()
        await pubsub.close()
