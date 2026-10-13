from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.graph.value_graph_traversal import ValueGraphTraversal
from app.repositories.value_graph_repository import ValueGraphRepository


router = APIRouter(
    prefix="/api/value-graphs",
    tags=["value-graphs"],
)

DATA_ROOT = Path(__file__).resolve().parents[3] / "data"

repository = ValueGraphRepository(DATA_ROOT)


@router.get("/{customer_id}")
def get_value_graph(customer_id: str):
    """Return the complete Value Graph for a customer."""
    try:
        graph = repository.load(customer_id)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Value graph not found for customer: {customer_id}",
        )

    return graph.model_dump()


@router.get("/{customer_id}/metrics/{metric_id}")
def get_metric(
    customer_id: str,
    metric_id: str,
):
    """Return a single metric."""
    try:
        metric = repository.get_metric(
            customer_id,
            metric_id,
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Value graph not found for customer: {customer_id}",
        )
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=f"Metric not found: {metric_id}",
        )

    return metric.model_dump()


@router.get("/{customer_id}/impact-path")
def get_impact_path(
    customer_id: str,
    source_metric_id: str,
    target_metric_id: str,
):
    """Return the causal impact path between two metrics."""
    try:
        graph = repository.load(customer_id)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Value graph not found for customer: {customer_id}",
        )

    traversal = ValueGraphTraversal(graph)

    try:
        path = traversal.find_impact_path(
            source_metric_id,
            target_metric_id,
        )
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    if not path:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No impact path found from "
                f"'{source_metric_id}' to "
                f"'{target_metric_id}'"
            ),
        )

    relationships = traversal.get_relationships_for_path(path)

    return {
        "customer_id": customer_id,
        "source_metric_id": source_metric_id,
        "target_metric_id": target_metric_id,
        "metrics": [
            metric.model_dump()
            for metric in path
        ],
        "relationships": [
            relationship.model_dump()
            for relationship in relationships
        ],
    }
