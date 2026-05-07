from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    """Shared state for the multi-agent system."""
    query: str
    original_query: str
    
    # Context and research
    internal_docs: List[Dict[str, Any]]
    web_results: List[Dict[str, Any]]
    merged_context: str
    sources: List[Dict[str, str]]
    
    # Agent outputs
    research_report: str
    risk_analysis: Dict[str, Any]
    audit_report: str
    final_report_md: str
    
    # Control flow & metadata
    next_step: str
    errors: List[str]
    iteration_count: int
    reflection_log: List[str]
