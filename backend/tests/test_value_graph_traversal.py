from pathlib import Path

from app.graph.value_graph_traversal import ValueGraphTraversal
from app.repositories.value_graph_repository import ValueGraphRepository


DATA_ROOT = Path(__file__).resolve().parents[2] / "data"


def create_traversal():
    repository = ValueGraphRepository(DATA_ROOT)
    graph = repository.load("starbucks")
    return ValueGraphTraversal(graph)


def test_immediate_downstream_metric():
    traversal = create_traversal()

    metrics = traversal.get_downstream_metrics(
        "network_availability"
    )

    assert len(metrics) == 1
    assert metrics[0].id == "digital_transaction_recovery"


def test_downstream_metric_ids():
    traversal = create_traversal()

    metric_ids = traversal.get_downstream_metric_ids(
        "recovered_transactions"
    )

    assert metric_ids == ["incremental_revenue"]


def test_full_downstream_trace():
    traversal = create_traversal()

    metrics = traversal.trace_downstream(
        "network_availability"
    )

    metric_ids = [metric.id for metric in metrics]

    assert metric_ids == [
        "digital_transaction_recovery",
        "recovered_transactions",
        "incremental_revenue",
        "ceo_revenue_growth",
    ]


def test_leaf_metric_has_no_downstream_metrics():
    traversal = create_traversal()

    metrics = traversal.get_downstream_metrics(
        "ceo_revenue_growth"
    )

    assert metrics == []


def test_unknown_metric_raises_error():
    traversal = create_traversal()

    try:
        traversal.trace_downstream("does_not_exist")
        assert False
    except KeyError:
        assert True
