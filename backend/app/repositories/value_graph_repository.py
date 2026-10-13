import json
from pathlib import Path

from app.models.value_graph import Metric, Relationship, ValueGraph


class ValueGraphRepository:
    """Repository for loading and querying customer Value Graphs."""

    def __init__(self, data_root: Path):
        self.data_root = Path(data_root)

    def load(self, customer_id: str) -> ValueGraph:
        """Load and validate a customer's Value Graph."""
        graph_path = (
            self.data_root
            / "customers"
            / customer_id
            / "value_graph.json"
        )

        if not graph_path.exists():
            raise FileNotFoundError(
                f"Value graph not found for customer: {customer_id}"
            )

        with graph_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return ValueGraph.model_validate(data)

    def get_metric(
        self,
        customer_id: str,
        metric_id: str,
    ) -> Metric:
        """Return a specific metric from a customer's graph."""
        graph = self.load(customer_id)

        for metric in graph.metrics:
            if metric.id == metric_id:
                return metric

        raise KeyError(
            f"Metric '{metric_id}' not found for customer '{customer_id}'"
        )

    def get_relationships(
        self,
        customer_id: str,
    ) -> list[Relationship]:
        """Return all relationships for a customer's graph."""
        graph = self.load(customer_id)
        return graph.relationships
