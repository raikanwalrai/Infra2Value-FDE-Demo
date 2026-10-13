from pydantic import BaseModel, Field


class ScenarioOverride(BaseModel):
    """
    A proposed change to one metric in the Value Graph.
    """

    metric_id: str = Field(
        min_length=1,
        description="ID of the Value Graph metric being changed.",
    )

    baseline_value: float = Field(
        description="Current baseline value of the metric.",
    )

    scenario_value: float = Field(
        description="Proposed value of the metric under the scenario.",
    )


class Scenario(BaseModel):
    """
    A named business-value scenario.

    A scenario may contain one or more metric overrides.
    """

    scenario_id: str = Field(
        min_length=1,
        description="Unique identifier for the scenario.",
    )

    name: str = Field(
        min_length=1,
        description="Human-readable scenario name.",
    )

    description: str = Field(
        default="",
        description="Business description of the scenario.",
    )

    overrides: list[ScenarioOverride] = Field(
        min_length=1,
        description="Metric changes introduced by the scenario.",
    )


class ScenarioMetricResult(BaseModel):
    """
    Comparison of a metric's baseline and scenario values.
    """

    metric_id: str

    baseline_value: float

    scenario_value: float

    delta: float


class ScenarioResult(BaseModel):
    """
    Structured result of evaluating a scenario.
    """

    scenario_id: str

    scenario_name: str

    metric_results: list[ScenarioMetricResult]

    baseline_annual_value: float

    scenario_annual_value: float

    annual_value_delta: float
