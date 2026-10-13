import pytest

from app.models.value_graph import (
    Metric,
    Relationship,
    ScenarioMapping,
    ValueGraph,
)
from app.value_engine.scenario_graph_propagator import (
    ScenarioGraphPropagator,
)


def test_propagates_target_based_mapping_across_graph_relationship():
    graph = ValueGraph(
        customer_id="test_customer",
        metrics=[
            Metric(
                id="source_metric",
                name="Source Metric",
                domain="test",
                layer="infrastructure",
                unit="%",
                current_value=99.5,
            ),
            Metric(
                id="target_metric",
                name="Target Metric",
                domain="test",
                layer="technical_kpi",
                unit="%",
                current_value=0.0,
            ),
        ],
        relationships=[
            Relationship(
                source_metric_id="source_metric",
                target_metric_id="target_metric",
                relationship_type="causes",
                coefficient=1.0,
                scenario_mapping=ScenarioMapping(
                    type="target_based",
                    source_baseline=99.5,
                    source_target=99.9,
                    target_value=0.40,
                ),
            )
        ],
    )

    propagator = ScenarioGraphPropagator(graph)

    target_metric, scenario_value = propagator.propagate(
        source_metric_id="source_metric",
        source_scenario_value=99.9,
    )

    assert target_metric.id == "target_metric"
    assert scenario_value == pytest.approx(0.40)


def test_propagates_proportional_mapping_across_graph_relationship():
    graph = ValueGraph(
        customer_id="test_customer",
        metrics=[
            Metric(
                id="latency",
                name="Application Latency",
                domain="application",
                layer="technical_kpi",
                unit="ms",
                current_value=300.0,
            ),
            Metric(
                id="conversion_rate",
                name="Conversion Rate",
                domain="commerce",
                layer="business_kpi",
                unit="%",
                current_value=5.0,
            ),
        ],
        relationships=[
            Relationship(
                source_metric_id="latency",
                target_metric_id="conversion_rate",
                relationship_type="influences",
                coefficient=-0.005,
                scenario_mapping=ScenarioMapping(
                    type="proportional",
                    source_baseline=300.0,
                    source_target=150.0,
                    target_value=-0.005,
                ),
            )
        ],
    )

    propagator = ScenarioGraphPropagator(graph)

    target_metric, scenario_value = propagator.propagate(
        source_metric_id="latency",
        source_scenario_value=200.0,
    )

    assert target_metric.id == "conversion_rate"
    assert scenario_value == pytest.approx(5.5)


def test_unknown_source_metric_fails():
    graph = ValueGraph(
        customer_id="test_customer",
        metrics=[],
        relationships=[],
    )

    propagator = ScenarioGraphPropagator(graph)

    with pytest.raises(ValueError, match="not found"):
        propagator.propagate(
            source_metric_id="does_not_exist",
            source_scenario_value=100.0,
        )


def test_missing_scenario_mapping_fails():
    graph = ValueGraph(
        customer_id="test_customer",
        metrics=[
            Metric(
                id="source_metric",
                name="Source Metric",
                domain="test",
                layer="infrastructure",
                unit="%",
                current_value=99.0,
            ),
            Metric(
                id="target_metric",
                name="Target Metric",
                domain="test",
                layer="technical_kpi",
                unit="%",
                current_value=10.0,
            ),
        ],
        relationships=[
            Relationship(
                source_metric_id="source_metric",
                target_metric_id="target_metric",
                relationship_type="causes",
                coefficient=1.0,
            )
        ],
    )

    propagator = ScenarioGraphPropagator(graph)

    with pytest.raises(ValueError, match="No scenario mapping"):
        propagator.propagate(
            source_metric_id="source_metric",
            source_scenario_value=100.0,
        )


def test_propagates_through_multiple_graph_relationships():
    graph = ValueGraph(
        customer_id="test_customer",
        metrics=[
            Metric(
                id="infrastructure_metric",
                name="Infrastructure Metric",
                domain="infrastructure",
                layer="infrastructure",
                unit="%",
                current_value=99.0,
            ),
            Metric(
                id="technical_kpi",
                name="Technical KPI",
                domain="technology",
                layer="technical_kpi",
                unit="%",
                current_value=0.0,
            ),
            Metric(
                id="business_kpi",
                name="Business KPI",
                domain="business",
                layer="business_kpi",
                unit="%",
                current_value=10.0,
            ),
            Metric(
                id="financial_outcome",
                name="Financial Outcome",
                domain="finance",
                layer="financial_outcome",
                unit="USD",
                current_value=1000.0,
            ),
        ],
        relationships=[
            Relationship(
                source_metric_id="infrastructure_metric",
                target_metric_id="technical_kpi",
                relationship_type="causes",
                coefficient=1.0,
                scenario_mapping=ScenarioMapping(
                    type="target_based",
                    source_baseline=99.0,
                    source_target=99.5,
                    target_value=20.0,
                ),
            ),
            Relationship(
                source_metric_id="technical_kpi",
                target_metric_id="business_kpi",
                relationship_type="influences",
                coefficient=1.0,
                scenario_mapping=ScenarioMapping(
                    type="proportional",
                    source_baseline=0.0,
                    source_target=20.0,
                    target_value=0.25,
                ),
            ),
            Relationship(
                source_metric_id="business_kpi",
                target_metric_id="financial_outcome",
                relationship_type="contributes_to",
                coefficient=1.0,
                scenario_mapping=ScenarioMapping(
                    type="proportional",
                    source_baseline=10.0,
                    source_target=15.0,
                    target_value=100.0,
                ),
            ),
        ],
    )

    propagator = ScenarioGraphPropagator(graph)

    results = propagator.propagate_path(
        source_metric_id="infrastructure_metric",
        source_scenario_value=99.5,
        target_metric_id="financial_outcome",
    )

    assert len(results) == 3

    technical_metric, technical_value = results[0]
    business_metric, business_value = results[1]
    financial_metric, financial_value = results[2]

    assert technical_metric.id == "technical_kpi"
    assert technical_value == pytest.approx(20.0)

    assert business_metric.id == "business_kpi"
    assert business_value == pytest.approx(15.0)

    assert financial_metric.id == "financial_outcome"
    assert financial_value == pytest.approx(1500.0)


def test_propagates_real_starbucks_value_graph():
    from pathlib import Path

    from app.repositories.value_graph_repository import (
        ValueGraphRepository,
    )

    data_root = Path(__file__).resolve().parents[2] / "data"

    repository = ValueGraphRepository(data_root)
    graph = repository.load("starbucks")

    propagator = ScenarioGraphPropagator(graph)

    results = propagator.propagate_path(
        source_metric_id="network_availability",
        source_scenario_value=99.9,
        target_metric_id="incremental_revenue",
    )

    assert len(results) == 3

    recovery_metric, recovery_value = results[0]
    transactions_metric, transactions_value = results[1]
    revenue_metric, revenue_value = results[2]

    assert recovery_metric.id == "digital_transaction_recovery"
    assert recovery_value == pytest.approx(0.40)

    assert transactions_metric.id == "recovered_transactions"
    assert transactions_value == pytest.approx(1600.0)

    assert revenue_metric.id == "incremental_revenue"
    assert revenue_value == pytest.approx(12800.0)
