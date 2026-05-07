"""
Analysis pipeline service.

Orchestrates a multi-step legal contract audit using a Multi-Agent system:
  1. Ingestion (Parsing document structure)
  2. Extraction (Identifying key clauses & entities)
  3. Legal Research (Tavily + Qdrant search)
  4. Risk Audit (Analyzing liabilities & red flags)
  5. Final Synthesis (Professional Markdown report)

Each step streams SSE progress events to the frontend.
Integrated with LangGraph for robust orchestration.
"""

from __future__ import annotations

import json
import logging
from typing import AsyncGenerator, Dict, Any

from app.agents.graph import multi_agent_graph
from app.agents.state import AgentState

logger = logging.getLogger(__name__)

async def run_pipeline(
    text: str,
    contract_type: str | None = None,
    user_type: str | None = None,
) -> AsyncGenerator[str, None]:
    """
    Run the full audit pipeline using the LangGraph orchestration layer,
    yielding SSE events for each step.
    """

    # 1. Initialize steps for the frontend UI
    steps = [
        {"id": "orchestrator", "label": "Orchestrator", "description": "Routing and planning search strategy"},
        {"id": "researcher", "label": "Hybrid Researcher", "description": "Querying Tavily and Qdrant"},
        {"id": "analyst", "label": "Risk Analyst", "description": "Extracting clauses and liabilities"},
        {"id": "auditor", "label": "Final Auditor", "description": "Synthesizing and auditing report"},
    ]
    yield _sse({"event": "steps_init", "data": {"steps": steps}})

    # 2. Setup initial state for LangGraph
    initial_state: AgentState = {
        "query": f"Analyze this {contract_type or 'contract'} for a {user_type or 'user'}.",
        "original_query": f"Full audit of contract ({contract_type or 'unknown type'})",
        "internal_docs": [],
        "web_results": [],
        "merged_context": text,
        "sources": [],
        "research_report": "",
        "risk_analysis": {},
        "audit_report": "",
        "final_report_md": "",
        "next_step": "",
        "errors": [],
        "iteration_count": 0,
        "reflection_log": []
    }

    # 3. Execute Graph with state updates
    try:
        # LangGraph can run nodes sequentially. We'll listen for state changes.
        # Note: In a production environment with complex streaming, you'd use a custom
        # callback or event handler. For now, we simulate the step progression.
        
        current_node = None
        final_risk_analysis = {}
        final_report = ""
        
        async for output in multi_agent_graph.astream(initial_state):
            # output is a dict where keys are node names and values are the state updates
            for node_name, state_update in output.items():
                logger.info(f"Pipeline Node: {node_name} finished.")
                
                # Map LangGraph nodes to frontend steps
                step_id = node_name # orchestrator, researcher, analyst, auditor
                
                # Mark previous step as completed if any
                if current_node:
                    yield _sse({"event": "step_update", "data": {"step_id": current_node, "status": "completed"}})
                
                # Mark current step as processing
                yield _sse({"event": "step_update", "data": {"step_id": step_id, "status": "processing"}})
                current_node = step_id

                # Stream specific content chunks based on the node
                if node_name == "orchestrator":
                    log = state_update.get("reflection_log", [])
                    content = log[-1] if log else "Orchestrating strategy..."
                    yield _sse({"event": "content_chunk", "data": {"chunk": content, "step_id": "orchestrator"}})
                
                elif node_name == "researcher":
                    content = state_update.get("research_report", "")
                    yield _sse({"event": "content_chunk", "data": {"chunk": content, "step_id": "researcher"}})
                
                elif node_name == "analyst":
                    risk_json = state_update.get("risk_analysis", {})
                    final_risk_analysis = risk_json
                    content = json.dumps(risk_json, indent=2)
                    yield _sse({"event": "content_chunk", "data": {"chunk": content, "step_id": "analyst"}})
                
                elif node_name == "auditor":
                    report_md = state_update.get("final_report_md", "")
                    final_report = report_md
                    yield _sse({"event": "content_chunk", "data": {"chunk": report_md, "step_id": "auditor"}})

        # Final completion for the last node
        if current_node:
            yield _sse({"event": "step_update", "data": {"step_id": current_node, "status": "completed"}})

        # Send the final 'done' event with the full report
        yield _sse({"event": "done", "data": {"risk_analysis": final_risk_analysis, "report": final_report}})

    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        if current_node:
            yield _sse({"event": "step_update", "data": {"step_id": current_node, "status": "error"}})
        yield _sse({"event": "error", "data": {"message": f"Multi-agent pipeline failed: {str(e)}"}})

def _sse(payload: dict) -> str:
    """Format a dict as an SSE data line."""
    return f"data: {json.dumps(payload)}\n\n"
