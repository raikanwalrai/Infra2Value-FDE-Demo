import pytest

from app.models.value_graph import ScenarioMapping
from app.value_engine.scenario_mapping import calculate_target_delta


def test_target_based_mapping_returns_delta_to_configured_target():
    mapping = ScenarioMapping(
        type="target_based",
        source_baseline=99.5,
        source_target=99.9,
        target_value=0.40,
    )

    result = calculate_target_delta(
        mapping=mapping,
        source_baseline=99.5,
        source_value=99.9,
        target_baseline=0.0,
    )

    assert result == pytest.approx(0.40)


def test_proportional_mapping_calculates_target_delta():
    mapping = ScenarioMapping(
        type="proportional",
        source_baseline=300.0,
        source_target=150.0,
        target_value=0.75,
    )

    result = calculate_target_delta(
        mapping=mapping,
        source_baseline=300.0,
        source_value=150.0,
        target_baseline=1.0,
    )

    assert result == pytest.approx(-112.5)


def test_proportional_mapping_with_improvement():
    mapping = ScenarioMapping(
        type="proportional",
        source_baseline=300.0,
        source_target=150.0,
        target_value=0.005,
    )

    result = calculate_target_delta(
        mapping=mapping,
        source_baseline=300.0,
        source_value=150.0,
        target_baseline=2.0,
    )

    assert result == pytest.approx(-0.75)


def test_target_based_mapping_with_nonzero_target_baseline():
    mapping = ScenarioMapping(
        type="target_based",
        source_baseline=99.5,
        source_target=99.9,
        target_value=0.40,
    )

    result = calculate_target_delta(
        mapping=mapping,
        source_baseline=99.5,
        source_value=99.9,
        target_baseline=0.10,
    )

    assert result == pytest.approx(0.30)


def test_proportional_mapping_zero_source_change_has_zero_delta():
    mapping = ScenarioMapping(
        type="proportional",
        source_baseline=300.0,
        source_target=150.0,
        target_value=0.75,
    )

    result = calculate_target_delta(
        mapping=mapping,
        source_baseline=300.0,
        source_value=300.0,
        target_baseline=0.50,
    )

    assert result == pytest.approx(0.0)


def test_proportional_mapping_can_model_latency_to_conversion_improvement():
    mapping = ScenarioMapping(
        type="proportional",
        source_baseline=300.0,
        source_target=150.0,
        target_value=-0.005,
    )

    result = calculate_target_delta(
        mapping=mapping,
        source_baseline=300.0,
        source_value=200.0,
        target_baseline=5.0,
    )

    target_scenario_value = 5.0 + result

    assert result == pytest.approx(0.5)
    assert target_scenario_value == pytest.approx(5.5)


def test_proportional_mapping_can_convert_recovery_rate_to_transactions():
    mapping = ScenarioMapping(
        type="proportional",
        source_baseline=0.0,
        source_target=0.40,
        target_value=4000.0,
    )

    result = calculate_target_delta(
        mapping=mapping,
        source_baseline=0.0,
        source_value=0.40,
        target_baseline=0.0,
    )

    assert result == pytest.approx(1600.0)


def test_proportional_mapping_can_convert_transactions_to_revenue():
    mapping = ScenarioMapping(
        type="proportional",
        source_baseline=0.0,
        source_target=1600.0,
        target_value=8.0,
    )

    result = calculate_target_delta(
        mapping=mapping,
        source_baseline=0.0,
        source_value=1600.0,
        target_baseline=0.0,
    )

    assert result == pytest.approx(12800.0)
