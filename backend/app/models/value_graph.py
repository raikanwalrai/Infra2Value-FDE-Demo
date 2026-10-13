from typing import Literal

from pydantic import BaseModel, Field


MetricLayer = Literal[
    "infrastructure",
    "technical_kpi",
    "business_kpi",
    "financial_outcome",
    "cxo_outcome",
]

RelationshipType = Literal[
    "causes",
    "influences",
    "enables",
    "contributes_to",
]


class Metric(BaseModel):
    id: str
    name: str
    description: str = ""
    domain: str
    layer: MetricLayer
    unit: str
    current_value: float
    target_value: float | None = None
    source: str = "customer_assumption"
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)


class ScenarioMapping(BaseModel):
    """Structured mapping between a source metric change and target value."""

    type: Literal["target_based", "proportional"]
    source_baseline: float
    source_target: float
    target_value: float

class Relationship(BaseModel):
    source_metric_id: str
    target_metric_id: str
    relationship_type: RelationshipType
    coefficient: float
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    assumption: str = ""
    scenario_mapping: ScenarioMapping | None = None


class ValueGraph(BaseModel):
    customer_id: str
    metrics: list[Metric]
    relationships: list[Relationship]
