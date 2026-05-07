import json
import logging
from typing import Dict, Any
from app.agents.state import AgentState
from app.services.llm import generate

logger = logging.getLogger(__name__)

class LegalRiskAnalyst:
    async def run(self, state: AgentState) -> AgentState:
        """Analyze legal risks based on research and document context."""
        logger.info("LegalRiskAnalyst: Analyzing risks")
        
        context = state.get("merged_context", "")
        research = state.get("research_report", "")
        query = state.get("original_query", "")

        prompt = f"""
        You are a Senior Legal Risk Analyst analyzing a contract with layout-aware extraction.
        Your task is to identify potential legal liabilities, regulatory red flags, and compliance obligations
        based on the provided context and research.

        The document may include:
        - Headers marked with ## prefix
        - Tables marked with === TABLES DETECTED ===
        - Page markers like --- Page N ---

        QUERY: {query}
        
        RESEARCH FINDINGS:
        {research}
        
        DOCUMENT CONTEXT:
        {context}

        INSTRUCTIONS:
        1. Identify Red Flags: Points of high risk or potential legal violation.
        2. Identify Penalties: Possible fines or legal consequences for non-compliance.
        3. Identify Obligations: Key actions the user must take to remain compliant.
        4. Categorize each risk as High, Medium, or Low.
        5. Use section headers and page markers when grounding findings.
        6. Inspect table content for fees, payment terms, limits of liability, and termination triggers.

        OUTPUT FORMAT:
        Return ONLY a JSON object with the following structure:
        {{
            "red_flags": [
                {{"issue": "...", "severity": "High/Med/Low", "description": "..."}}
            ],
            "penalties": [
                {{"type": "...", "severity": "High/Med/Low", "impact": "..."}}
            ],
            "obligations": [
                {{"task": "...", "deadline": "...", "description": "..."}}
            ],
            "summary": "..."
        }}
        """

        response = await generate(prompt, system_prompt="You are a meticulous Legal Risk Analyst. Return JSON only.")
        
        try:
            # Clean up response in case of markdown blocks
            clean_response = response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:-3].strip()
            elif clean_response.startswith("```"):
                clean_response = clean_response[3:-3].strip()
                
            risk_analysis = json.loads(clean_response)
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Failed to parse risk analysis JSON: {e}")
            risk_analysis = {
                "error": "Failed to parse analysis",
                "raw_output": response,
                "red_flags": [],
                "penalties": [],
                "obligations": [],
                "summary": "Analysis failed to format correctly."
            }

        return {
            **state,
            "risk_analysis": risk_analysis
        }
