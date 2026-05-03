"""Analysis pipeline schemas — aligned to frontend AnalysisStep, RiskMatrix, ContractReport."""

from __future__ import annotations
from enum import Enum
from typing import Optional, List, Dict
from pydantic import BaseModel, Field

from .chat import ContractType, ReportVerdict


# ─── Analysis Pipeline Steps ───────────────────────────────

class StepStatus(str, Enum):
    IDLE = "idle"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


class AnalysisStepOut(BaseModel):
    id: str
    label: str
    description: str
    status: StepStatus


# ─── Risk Assessment ───────────────────────────────────────

class RiskLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RiskItemOut(BaseModel):
    id: str
    clause: str
    section: str
    level: RiskLevel
    description: str
    suggestion: Optional[str] = None
    industry_standard: Optional[str] = Field(None, serialization_alias="industryStandard")
    original_text: Optional[str] = Field(None, serialization_alias="originalText")

    model_config = {"populate_by_name": True}


class RiskMatrixOut(BaseModel):
    critical: List[RiskItemOut] = []
    high: List[RiskItemOut] = []
    medium: List[RiskItemOut] = []
    low: List[RiskItemOut] = []


# ─── Red Flags & Recommendations ───────────────────────────

class RedFlagOut(BaseModel):
    id: str
    title: str
    description: str
    section: str
    severity: RiskLevel


class RecommendationOut(BaseModel):
    id: str
    for_attorneys: str = Field(serialization_alias="forAttorneys")
    for_individuals: str = Field(serialization_alias="forIndividuals")

    model_config = {"populate_by_name": True}


# ─── Appendix ──────────────────────────────────────────────

class GlossaryItem(BaseModel):
    term: str
    definition: str


class LegalReference(BaseModel):
    title: str
    citation: str


class BenchmarkItem(BaseModel):
    metric: str
    value: str
    comparison: str


class AppendixOut(BaseModel):
    glossary: List[GlossaryItem] = []
    legal_references: List[LegalReference] = Field([], serialization_alias="legalReferences")
    benchmarks: List[BenchmarkItem] = []

    model_config = {"populate_by_name": True}


# ─── Full Contract Report ──────────────────────────────────

class ContractReportOut(BaseModel):
    verdict: ReportVerdict
    contract_type: ContractType = Field(serialization_alias="contractType")
    executive_summary: str = Field(serialization_alias="executiveSummary")
    risk_matrix: RiskMatrixOut = Field(serialization_alias="riskMatrix")
    red_flags: List[RedFlagOut] = Field([], serialization_alias="redFlags")
    recommendations: List[RecommendationOut] = []
    appendix: AppendixOut = AppendixOut()

    model_config = {"populate_by_name": True}


# ─── SSE Stream Events ─────────────────────────────────────

class SSEEventType(str, Enum):
    STEP_UPDATE = "step_update"
    CONTENT_CHUNK = "content_chunk"
    REPORT = "report"
    ERROR = "error"
    DONE = "done"


class SSEEvent(BaseModel):
    event: SSEEventType
    data: Dict
