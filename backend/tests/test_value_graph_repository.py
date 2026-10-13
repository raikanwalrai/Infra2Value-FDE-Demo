from pathlib import Path

import pytest

from app.models.value_graph import Metric, Relationship, ValueGraph
from app.repositories.value_graph_repository import ValueGraphRepository


DATA_ROOT = Path(__file__).resolve().parents[2] / "data"


def test_load_starbucks_value_graph():
    repository = ValueGraphRepository(DATA_ROOT)

    graph = repository.load("starbucks")

    assert isinstance(graph, ValueGraph)
    assert graph.customer_id == "starbucks"
    assert len(graph.metrics) == 5
    assert len(graph.relationships) == 4


def test_get_metric():
    repository = ValueGraphRepository(DATA_ROOT)

    metric = repository.get_metric(
        "starbucks",
        "network_availability",
    )

    assert isinstance(metric, Metric)
    assert metric.name == "Network Availability"
    assert metric.current_value == 99.5
    assert metric.target_value == 99.9


def test_get_relationships():
    repository = ValueGraphRepository(DATA_ROOT)

    relationships = repository.get_relationships("starbucks")

    assert len(relationships) == 4
    assert all(isinstance(r, Relationship) for r in relationships)


def test_missing_customer():
    repository = ValueGraphRepository(DATA_ROOT)

    with pytest.raises(FileNotFoundError):
        repository.load("unknown_customer")


def test_missing_metric():
    repository = ValueGraphRepository(DATA_ROOT)

    with pytest.raises(KeyError):
        repository.get_metric(
            "starbucks",
            "does_not_exist",
        )
