from app.models.value_graph import Metric, Relationship, ValueGraph


class ValueGraphTraversal:
    """Traverse causal relationships within a Value Graph."""

    def __init__(self, graph: ValueGraph):
        self.graph = graph

        self._metrics = {
            metric.id: metric
            for metric in graph.metrics
        }

        self._relationships = {
            (
                relationship.source_metric_id,
                relationship.target_metric_id,
            ): relationship
            for relationship in graph.relationships
        }

        self._downstream = {}

        for relationship in graph.relationships:
            self._downstream.setdefault(
                relationship.source_metric_id,
                [],
            ).append(relationship.target_metric_id)

    def get_metric(self, metric_id: str) -> Metric:
        """Return a metric by ID."""
        if metric_id not in self._metrics:
            raise KeyError(f"Metric not found: {metric_id}")

        return self._metrics[metric_id]

    def get_relationship(
        self,
        source_metric_id: str,
        target_metric_id: str,
    ) -> Relationship:
        """Return the relationship connecting two metrics."""
        key = (source_metric_id, target_metric_id)

        if key not in self._relationships:
            raise KeyError(
                f"No relationship exists from "
                f"'{source_metric_id}' to '{target_metric_id}'"
            )

        return self._relationships[key]

    def get_downstream_metric_ids(
        self,
        metric_id: str,
    ) -> list[str]:
        """Return immediate downstream metric IDs."""
        if metric_id not in self._metrics:
            raise KeyError(f"Metric not found: {metric_id}")

        return self._downstream.get(metric_id, [])

    def get_downstream_metrics(
        self,
        metric_id: str,
    ) -> list[Metric]:
        """Return immediate downstream Metric objects."""
        return [
            self._metrics[target_id]
            for target_id in self.get_downstream_metric_ids(metric_id)
        ]

    def trace_downstream(
        self,
        metric_id: str,
    ) -> list[Metric]:
        """
        Traverse all downstream metrics using breadth-first search.

        The starting metric itself is not included.
        """
        if metric_id not in self._metrics:
            raise KeyError(f"Metric not found: {metric_id}")

        visited = set()
        queue = list(self.get_downstream_metric_ids(metric_id))
        result = []

        while queue:
            current_id = queue.pop(0)

            if current_id in visited:
                continue

            visited.add(current_id)
            result.append(self._metrics[current_id])

            queue.extend(
                self.get_downstream_metric_ids(current_id)
            )

        return result

    def find_impact_path(
        self,
        source_metric_id: str,
        target_metric_id: str,
    ) -> list[Metric]:
        """
        Find a causal path between two metrics.

        The returned path includes both source and target.
        Returns an empty list if no path exists.
        """
        if source_metric_id not in self._metrics:
            raise KeyError(f"Metric not found: {source_metric_id}")

        if target_metric_id not in self._metrics:
            raise KeyError(f"Metric not found: {target_metric_id}")

        queue = [source_metric_id]
        parent = {source_metric_id: None}

        while queue:
            current_id = queue.pop(0)

            if current_id == target_metric_id:
                break

            for next_id in self.get_downstream_metric_ids(current_id):
                if next_id not in parent:
                    parent[next_id] = current_id
                    queue.append(next_id)

        if target_metric_id not in parent:
            return []

        path_ids = []
        current_id = target_metric_id

        while current_id is not None:
            path_ids.append(current_id)
            current_id = parent[current_id]

        path_ids.reverse()

        return [
            self._metrics[metric_id]
            for metric_id in path_ids
        ]

    def get_relationships_for_path(
        self,
        path: list[Metric],
    ) -> list[Relationship]:
        """Return relationships connecting consecutive metrics."""
        relationships = []

        for source, target in zip(path, path[1:]):
            relationships.append(
                self.get_relationship(
                    source.id,
                    target.id,
                )
            )

        return relationships
