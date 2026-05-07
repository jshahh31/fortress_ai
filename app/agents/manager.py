import logging
from app.agents.state import AgentState
from app.services.llm import generate

logger = logging.getLogger(__name__)

class Orchestrator:
    async def run(self, state: AgentState) -> AgentState:
        """Route the query and decide on data sources."""
        logger.info(f"Orchestrator: Routing query '{state['query']}'")

        prompt = f"""
        You are the Manager Agent for Fortress AI. Your job is to analyze the user's legal query 
        and decide on the best research strategy.

        QUERY: {state['query']}

        DECISION TASKS:
        1. Rewrite the query for optimal vector and web search.
        2. Decide if we need:
           - INTERNAL: Search private legal documents in Qdrant.
           - WEB: Search real-time legal web data via Tavily.
           - BOTH: Recommended for most legal inquiries.

        OUTPUT FORMAT:
        Return ONLY a JSON object:
        {{
            "optimized_query": "...",
            "strategy": "INTERNAL | WEB | BOTH",
            "reasoning": "..."
        }}
        """

        response = await generate(prompt, system_prompt="You are a strategic legal orchestrator. Return JSON.")
        
        # Simple extraction logic for the demo, can be improved with a proper parser
        import json
        try:
            clean_response = response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:-3].strip()
            decision = json.loads(clean_response)
            
            optimized_query = decision.get("optimized_query", state["query"])
            strategy = decision.get("strategy", "BOTH")
        except:
            optimized_query = state["query"]
            strategy = "BOTH"

        return {
            **state,
            "query": optimized_query,
            "next_step": "researcher", # Control flow indicator
            "reflection_log": state.get("reflection_log", []) + [f"Orchestrator chose {strategy} strategy."]
        }
