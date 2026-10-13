from pydantic import BaseModel


class ImpactStep(BaseModel):
    source_metric_id: str
    target_metric_id: str
    relationship_type: str
    coefficient: float
    assumption: str
    confidence: float


class ValueImpactResult(BaseModel):
    customer_id: str

    source_metric_id: str
    target_metric_id: str

    metric_path: list[str]

    impact_steps: list[ImpactStep]

    recovered_transactions_per_month: float
    incremental_revenue_per_month: float
    incremental_revenue_per_year: float
