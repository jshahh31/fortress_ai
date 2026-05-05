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

async def research_node(state: AuditState) -> AuditState:
    """Queries Qdrant for precedents using Qwen (mocked for now)."""
    # In a real scenario, we'd use bge-m3 to embed state['extracted_data'] and query Qdrant.
    messages = [
        SystemMessage(content="You are a legal researcher AI. Summarize relevant legal precedents based on the extracted data."),
        HumanMessage(content=f"Extracted data:\n{state['extracted_data']}")
    ]
    response = await qwen_llm.ainvoke(messages)
    return {"research_findings": [response.content], "gpu_id": "GPU 0 (Qwen)"}

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
