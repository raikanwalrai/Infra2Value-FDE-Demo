from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


Severity = Literal["critical", "high", "medium", "low"]
IncidentStatus = Literal["open", "investigating", "resolved"]
EvidenceKind = Literal["metric", "log", "event", "transaction"]
EvidenceStatus = Literal["observed", "inferred"]


class EvidenceItem(BaseModel):
    id: str
    kind: EvidenceKind
    source: str
    observed_at: datetime
    title: str
    description: str = ""
    status: EvidenceStatus = "observed"
    metric_name: str | None = None
    value: float | None = None
    unit: str | None = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    related_metric_ids: list[str] = Field(default_factory=list)


class Incident(BaseModel):
    id: str
    customer_id: str
    title: str
    summary: str
    severity: Severity
    status: IncidentStatus = "open"
    started_at: datetime
    evidence: list[EvidenceItem] = Field(default_factory=list)
