import json
from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from app.core.config import settings

# Define the State
class AuditState(TypedDict):
    document_id: str
    text: str
    extracted_data: Dict[str, Any]
    research_findings: List[str]
    risk_assessment: Dict[str, Any]
    final_report: str
    gpu_id: str  # Metadata tracking the GPU used

# Initialize the LLM pointing to the vLLM endpoint
qwen_llm = ChatOpenAI(
    model=settings.QWEN_MODEL,
    openai_api_key=settings.LOCAL_API_KEY,
    openai_api_base=settings.QWEN_API_BASE,
    max_tokens=4096,
)

async def extraction_node(state: AuditState) -> AuditState:
    """Extracts raw text and metadata using Qwen."""
    messages = [
        SystemMessage(content="You are an expert legal data extraction AI. Extract key entities and clauses into JSON."),
        HumanMessage(content=f"Extract data from this text:\n\n{state['text']}")
    ]
    response = await qwen_llm.ainvoke(messages)
    
    # Mocking JSON parsing for boilerplate
    try:
        extracted_data = json.loads(response.content)
    except json.JSONDecodeError:
        extracted_data = {"raw_extraction": response.content}
        
    return {"extracted_data": extracted_data, "gpu_id": "GPU 0 (Qwen)"}

from app.services.search import search_service
from app.services.vector_db import vector_db

async def research_node(state: AuditState) -> AuditState:
    """Queries both Web (Tavily) and Internal DB (Qdrant) for a complete legal context."""
    
    # 1. Ask Qwen to generate a search query
    query_msg = [
        SystemMessage(content="You are a legal researcher. Generate a single precise search query to find relevant laws or precedents. Return ONLY the query string."),
        HumanMessage(content=f"Contract Data:\n{state['extracted_data']}")
    ]
    query_resp = await qwen_llm.ainvoke(query_msg)
    search_query = query_resp.content.strip().strip('"')

    # 2. Perform Web Search (External Knowledge)
    web_results = await search_service.search(search_query)
    web_context = "\n\n".join([f"Web Source: {r['url']}\nContent: {r['content']}" for r in web_results])

    # 3. Perform Qdrant Search (Internal Precedents)
    try:
        internal_results = await vector_db.search(search_query, limit=3)
        internal_context = "\n\n".join([f"Internal Precedent: {r.get('filename', 'Unknown')}\nContent: {r.get('content', '')}" for r in internal_results])
    except Exception as e:
        logger.warning(f"Qdrant search failed: {e}")
        internal_context = "No internal precedents found."

    # 4. Summarize findings from both sources
    summary_msg = [
        SystemMessage(content="You are a legal researcher AI. Summarize the following findings from both Web Search and Internal Precedents. Highlight any conflicts between current law and historical company practices."),
        HumanMessage(content=f"QUERY: {search_query}\n\nWEB FINDINGS:\n{web_context}\n\nINTERNAL FINDINGS:\n{internal_context}")
    ]
    response = await qwen_llm.ainvoke(summary_msg)
    
    return {"research_findings": [response.content], "gpu_id": "GPU 0 (Qwen + Web + Qdrant)"}

async def risk_node(state: AuditState) -> AuditState:
    """Evaluates risks using Qwen."""
    messages = [
        SystemMessage(content="You are a legal risk assessor. Identify liabilities and assign a risk level (High, Medium, Low). Return as JSON."),
        HumanMessage(content=f"Data:\n{state['extracted_data']}\n\nResearch:\n{state['research_findings']}")
    ]
    response = await qwen_llm.ainvoke(messages)
    try:
        risk_data = json.loads(response.content)
    except json.JSONDecodeError:
        risk_data = {"risk_level": "Unknown", "description": response.content, "affected_clauses": []}
        
    return {"risk_assessment": risk_data, "gpu_id": "GPU 0 (Qwen)"}

async def reporter_node(state: AuditState) -> AuditState:
    """Synthesizes the final report using Qwen."""
    # This node will be used in the streaming endpoint as well
    messages = [
        SystemMessage(content="You are a senior legal reporter. Write a professional audit report based on the findings."),
        HumanMessage(content=f"Extracted: {state['extracted_data']}\nRisk: {state['risk_assessment']}")
    ]
    response = await qwen_llm.ainvoke(messages)
    return {"final_report": response.content, "gpu_id": "GPU 0 (Qwen)"}

# Build the Graph
workflow = StateGraph(AuditState)

workflow.add_node("extraction", extraction_node)
workflow.add_node("research", research_node)
workflow.add_node("risk", risk_node)
workflow.add_node("reporter", reporter_node)

workflow.set_entry_point("extraction")
workflow.add_edge("extraction", "research")
workflow.add_edge("research", "risk")
workflow.add_edge("risk", "reporter")
workflow.add_edge("reporter", END)

app_graph = workflow.compile()
