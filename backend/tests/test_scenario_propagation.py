import pytest

from app.models.value_graph import ScenarioMapping
from app.value_engine.scenario_propagation import propagate_metric_value


def test_propagate_target_based_mapping():
    mapping = ScenarioMapping(
        type="target_based",
        source_baseline=99.5,
        source_target=99.9,
        target_value=0.40,
    )

    result = propagate_metric_value(
        mapping=mapping,
        source_baseline=99.5,
        source_value=99.9,
        target_baseline=0.0,
    )

    assert result == pytest.approx(0.40)


def test_propagate_target_based_mapping_with_nonzero_target_baseline():
    mapping = ScenarioMapping(
        type="target_based",
        source_baseline=99.5,
        source_target=99.9,
        target_value=0.40,
    )

    result = propagate_metric_value(
        mapping=mapping,
        source_baseline=99.5,
        source_value=99.9,
        target_baseline=0.10,
    )

    assert result == pytest.approx(0.40)


def test_propagate_proportional_mapping():
    mapping = ScenarioMapping(
        type="proportional",
        source_baseline=300.0,
        source_target=150.0,
        target_value=-0.005,
    )

    result = propagate_metric_value(
        mapping=mapping,
        source_baseline=300.0,
        source_value=200.0,
        target_baseline=5.0,
    )

    assert result == pytest.approx(5.5)


def test_proportional_mapping_with_no_source_change():
    mapping = ScenarioMapping(
        type="proportional",
        source_baseline=300.0,
        source_target=150.0,
        target_value=-0.005,
    )

    result = propagate_metric_value(
        mapping=mapping,
        source_baseline=300.0,
        source_value=300.0,
        target_baseline=5.0,
    )

    assert result == pytest.approx(5.0)
