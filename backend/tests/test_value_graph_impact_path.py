from pathlib import Path

from app.graph.value_graph_traversal import ValueGraphTraversal
from app.repositories.value_graph_repository import ValueGraphRepository


DATA_ROOT = Path(__file__).resolve().parents[2] / "data"


def create_traversal():
    repository = ValueGraphRepository(DATA_ROOT)
    graph = repository.load("starbucks")
    return ValueGraphTraversal(graph)


def test_find_revenue_impact_path():
    traversal = create_traversal()

    path = traversal.find_impact_path(
        "network_availability",
        "incremental_revenue",
    )

    path_ids = [metric.id for metric in path]

    assert path_ids == [
        "network_availability",
        "digital_transaction_recovery",
        "recovered_transactions",
        "incremental_revenue",
    ]


def test_find_cxo_impact_path():
    traversal = create_traversal()

    path = traversal.find_impact_path(
        "network_availability",
        "ceo_revenue_growth",
    )

    path_ids = [metric.id for metric in path]

    assert path_ids == [
        "network_availability",
        "digital_transaction_recovery",
        "recovered_transactions",
        "incremental_revenue",
        "ceo_revenue_growth",
    ]


def test_relationships_for_path():
    traversal = create_traversal()

    path = traversal.find_impact_path(
        "network_availability",
        "incremental_revenue",
    )

    relationships = traversal.get_relationships_for_path(path)

    assert len(relationships) == 3

    assert relationships[0].relationship_type == "causes"
    assert relationships[1].relationship_type == "causes"
    assert relationships[2].relationship_type == "contributes_to"


def test_no_impact_path():
    traversal = create_traversal()

    path = traversal.find_impact_path(
        "ceo_revenue_growth",
        "network_availability",
    )

    assert path == []
