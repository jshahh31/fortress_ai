"""Health check route."""

from fastapi import APIRouter

from app.services import llm

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Basic health check."""
    return {"status": "healthy", "service": "Fortress AI Backend"}


@router.get("/health/llm")
async def llm_health():
    """Check LLM endpoint connectivity (calls each model with a tiny prompt)."""
    results = await llm.check_connectivity()
    all_ok = all(results.values())
    return {
        "status": "healthy" if all_ok else "degraded",
        "models": results,
    }
