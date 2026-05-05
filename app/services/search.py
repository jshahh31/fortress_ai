import os
import logging
from typing import List, Dict, Any
import httpx

logger = logging.getLogger(__name__)

class SearchService:
    """Service for web searching using Tavily (LLM-optimized search)."""
    
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        self.base_url = "https://api.tavily.com/search"

    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Perform a web search and return results."""
        if not self.api_key:
            logger.warning("TAVILY_API_KEY not set. Returning mock results.")
            return [{"title": "Search Disabled", "url": "", "content": "TAVILY_API_KEY is missing."}]

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    json={
                        "api_key": self.api_key,
                        "query": query,
                        "search_depth": "advanced",
                        "max_results": max_results,
                    },
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
                return data.get("results", [])
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

# Singleton instance
search_service = SearchService()
