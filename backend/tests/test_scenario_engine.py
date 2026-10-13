from pathlib import Path

import pytest

from app.models.value_graph import ScenarioMapping
from app.models.value_graph import Relationship
from app.value_engine.scenario_engine import ScenarioEngine
from app.value_engine.scenario_models import Scenario, ScenarioOverride


DATA_ROOT = Path(__file__).resolve().parents[2] / "data"


def test_scenario_engine_calculates_starbucks_availability_scenario():
    engine = ScenarioEngine(DATA_ROOT)

    scenario = Scenario(
        scenario_id="availability_001",
        name="Improve Network Availability",
        description="Improve network availability from 99.5% to 99.9%.",
        overrides=[
            ScenarioOverride(
                metric_id="network_availability",
                baseline_value=99.5,
                scenario_value=99.9,
            )
        ],
    )

    result = engine.evaluate_scenario("starbucks", scenario)

    assert result.scenario_id == "availability_001"
    assert result.scenario_name == "Improve Network Availability"

    assert result.baseline_annual_value == 0.0
    assert result.scenario_annual_value == 153600.0
    assert result.annual_value_delta == 153600.0


def test_scenario_engine_calculates_metric_delta():
    engine = ScenarioEngine(DATA_ROOT)

    scenario = Scenario(
        scenario_id="availability_002",
        name="Availability Improvement",
        overrides=[
            ScenarioOverride(
                metric_id="network_availability",
                baseline_value=99.5,
                scenario_value=99.9,
            )
        ],
    )

    result = engine.evaluate_scenario("starbucks", scenario)

    metric_result = result.metric_results[0]

    assert metric_result.metric_id == "network_availability"
    assert metric_result.baseline_value == 99.5
    assert metric_result.scenario_value == 99.9
    assert metric_result.delta == pytest.approx(0.4)


def test_scenario_engine_rejects_unknown_metric():
    engine = ScenarioEngine(DATA_ROOT)

    scenario = Scenario(
        scenario_id="availability_003",
        name="Invalid Scenario",
        overrides=[
            ScenarioOverride(
                metric_id="unknown_metric",
                baseline_value=0.0,
                scenario_value=1.0,
            )
        ],
    )

    with pytest.raises(ValueError, match="unknown_metric"):
        engine.evaluate_scenario("starbucks", scenario)


def test_scenario_mapping_is_available_on_starbucks_relationship():
    from app.repositories.value_graph_repository import ValueGraphRepository

    repository = ValueGraphRepository(DATA_ROOT)
    graph = repository.load("starbucks")

    relationship = next(
        relationship
        for relationship in graph.relationships
        if relationship.target_metric_id == "digital_transaction_recovery"
    )

    assert relationship.scenario_mapping is not None
    assert isinstance(relationship.scenario_mapping, ScenarioMapping)
    assert relationship.scenario_mapping.source_baseline == 99.5
    assert relationship.scenario_mapping.source_target == 99.9
    assert relationship.scenario_mapping.target_value == 0.40
