from app.models.value_graph import Metric, Relationship, ScenarioMapping, ValueGraph


def test_metric_model():
    metric = Metric(
        id="network_availability",
        name="Network Availability",
        domain="network",
        layer="infrastructure",
        unit="%",
        current_value=99.5,
        target_value=99.9,
        confidence=0.8,
    )

    assert metric.id == "network_availability"
    assert metric.current_value == 99.5
    assert metric.target_value == 99.9


def test_relationship_model():
    relationship = Relationship(
        source_metric_id="network_availability",
        target_metric_id="digital_transaction_recovery",
        relationship_type="influences",
        coefficient=0.40,
        confidence=0.65,
    )

    assert relationship.coefficient == 0.40
    assert relationship.confidence == 0.65


def test_value_graph_model():
    metric = Metric(
        id="network_availability",
        name="Network Availability",
        domain="network",
        layer="infrastructure",
        unit="%",
        current_value=99.5,
        target_value=99.9,
    )

    graph = ValueGraph(
        customer_id="starbucks",
        metrics=[metric],
        relationships=[],
    )

    assert graph.customer_id == "starbucks"
    assert len(graph.metrics) == 1


def test_scenario_mapping_model():
    mapping = ScenarioMapping(
        type="target_based",
        source_baseline=99.5,
        source_target=99.9,
        target_value=0.40,
    )

    assert mapping.type == "target_based"
    assert mapping.source_baseline == 99.5
    assert mapping.source_target == 99.9
    assert mapping.target_value == 0.40


def test_relationship_with_scenario_mapping():
    relationship = Relationship(
        source_metric_id="network_availability",
        target_metric_id="digital_transaction_recovery",
        relationship_type="causes",
        coefficient=0.40,
        confidence=0.65,
        scenario_mapping=ScenarioMapping(
            type="target_based",
            source_baseline=99.5,
            source_target=99.9,
            target_value=0.40,
        ),
    )

    assert relationship.scenario_mapping is not None
    assert relationship.scenario_mapping.target_value == 0.40


def test_proportional_scenario_mapping_model():
    mapping = ScenarioMapping(
        type="proportional",
        source_baseline=300.0,
        source_target=150.0,
        target_value=0.75,
    )

    assert mapping.type == "proportional"
    assert mapping.source_baseline == 300.0
    assert mapping.source_target == 150.0
    assert mapping.target_value == 0.75
