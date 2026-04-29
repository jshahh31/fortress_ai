import asyncio
import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from app.db.qdrant import init_qdrant
from app.agents.graph import app_graph, gemma_llm, AuditState
from app.schemas.document import AuditRequest
from langchain_core.messages import HumanMessage, SystemMessage

app = FastAPI(title="Fortress AI", description="Private Multi-Agent Legal Audit System")

@app.on_event("startup")
async def startup_event():
    # Initialize Qdrant collection on startup
    await init_qdrant()

@app.post("/audit")
async def run_audit(request: AuditRequest):
    """Runs the full async LangGraph workflow."""
    initial_state = AuditState(
        document_id=request.document_id,
        text=request.text,
        extracted_data={},
        research_findings=[],
        risk_assessment={},
        final_report="",
        gpu_id=""
    )
    
    # Run the graph asynchronously
    final_state = await app_graph.ainvoke(initial_state)
    return final_state

@app.post("/audit/stream")
async def stream_audit_report(request: AuditRequest):
    """
    Runs the graph up to Risk, then streams the final report from the Reporter node using Gemma.
    Demonstrates word-by-word streaming for the UI.
    """
    initial_state = AuditState(
        document_id=request.document_id,
        text=request.text,
        extracted_data={},
        research_findings=[],
        risk_assessment={},
        final_report="",
        gpu_id=""
    )
    
    # We could stream from the graph directly, but for clarity and simplicity in this boilerplate, 
    # we'll execute up to risk manually or run the whole graph and just stream the last part.
    # To properly stream the LLM in LangGraph, you yield from astream_events.
    # Here, we will just stream the gemma response directly for the reporter phase.
    
    async def report_generator():
        # First, run the graph async to get the pre-requisite state
        state = await app_graph.ainvoke(initial_state)
        
        yield "data: {\"status\": \"Extraction, Research, Risk completed. Generating Report...\"}\n\n"
        
        messages = [
            SystemMessage(content="You are a senior legal reporter. Write a professional audit report based on the findings."),
            HumanMessage(content=f"Extracted: {state['extracted_data']}\nRisk: {state['risk_assessment']}")
        ]
        
        # Stream the response word-by-word from Gemma
        async for chunk in gemma_llm.astream(messages):
            if chunk.content:
                # SSE format
                yield f"data: {json.dumps({'chunk': chunk.content, 'gpu_id': 'GPU 1 (Gemma)'})}\n\n"
        
        yield "data: [DONE]\n\n"
        
    return StreamingResponse(report_generator(), media_type="text/event-stream")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
