from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class DocumentChunk(BaseModel):
    id: str
    text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class RiskAssessment(BaseModel):
    risk_level: str = Field(description="High, Medium, or Low")
    description: str
    affected_clauses: List[str]

class AuditReport(BaseModel):
    document_id: str
    summary: str
    risks: List[RiskAssessment]
    recommendations: List[str]
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AuditRequest(BaseModel):
    document_id: str
    text: str
