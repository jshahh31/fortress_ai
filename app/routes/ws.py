import json
import logging
import jwt
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.services.pubsub import get_subscriber
from app.core.config import settings

from jwt import PyJWKClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["WebSocket"])

# Initialize JWK client with caching
jwks_client = PyJWKClient(settings.CLERK_JWKS_URL)

async def verify_clerk_token(token: str) -> str:
    """
    Validate the Clerk JWT token using RS256 signature verification.
    """
    if not token:
        raise ValueError("No token provided")
    
    try:
        # Get the signing key from the JWKS endpoint
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        
        # Decode and verify the token
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=settings.CLERK_ISSUER,
        )
        
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Token does not contain a user ID (sub).")
        return user_id
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired.")
    except jwt.InvalidTokenError as e:
        raise ValueError(f"Invalid token: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error during token validation: {e}")
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
