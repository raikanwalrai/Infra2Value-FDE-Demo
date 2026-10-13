import pytest
from pydantic import ValidationError

from app.value_engine.scenario_models import (
    Scenario,
    ScenarioMetricResult,
    ScenarioOverride,
    ScenarioResult,
)


def test_scenario_override():
    override = ScenarioOverride(
        metric_id="network_availability",
        baseline_value=99.5,
        scenario_value=99.9,
    )

    assert override.metric_id == "network_availability"
    assert override.baseline_value == pytest.approx(99.5)
    assert override.scenario_value == pytest.approx(99.9)


def test_scenario():
    scenario = Scenario(
        scenario_id="network_resilience",
        name="Network Resilience Improvement",
        description="Improve network availability.",
        overrides=[
            ScenarioOverride(
                metric_id="network_availability",
                baseline_value=99.5,
                scenario_value=99.9,
            )
        ],
    )

    assert scenario.scenario_id == "network_resilience"
    assert scenario.name == "Network Resilience Improvement"
    assert len(scenario.overrides) == 1


def test_scenario_requires_at_least_one_override():
    with pytest.raises(ValidationError):
        Scenario(
            scenario_id="empty_scenario",
            name="Empty Scenario",
            overrides=[],
        )


def test_scenario_metric_result():
    result = ScenarioMetricResult(
        metric_id="network_availability",
        baseline_value=99.5,
        scenario_value=99.9,
        delta=0.4,
    )

    assert result.delta == pytest.approx(0.4)


def test_scenario_result():
    result = ScenarioResult(
        scenario_id="network_resilience",
        scenario_name="Network Resilience Improvement",
        metric_results=[
            ScenarioMetricResult(
                metric_id="network_availability",
                baseline_value=99.5,
                scenario_value=99.9,
                delta=0.4,
            )
        ],
        baseline_annual_value=0,
        scenario_annual_value=153600,
        annual_value_delta=153600,
    )

    assert result.scenario_id == "network_resilience"
    assert result.scenario_annual_value == pytest.approx(153600)
    assert result.annual_value_delta == pytest.approx(153600)
