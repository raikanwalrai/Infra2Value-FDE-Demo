from app.models.value_graph import Metric, ValueGraph
from app.value_engine.scenario_propagation import propagate_metric_value


class ScenarioGraphPropagator:
    """
    Propagates scenario values across Value Graph relationships.

    This component contains no business-specific metric IDs.
    """

    def __init__(self, graph: ValueGraph):
        self.graph = graph

    def propagate(
        self,
        source_metric_id: str,
        source_scenario_value: float,
    ) -> tuple[Metric, float]:
        """
        Propagate a scenario value across one outgoing relationship.
        """

        source_metric = self._get_metric(source_metric_id)

        relationship = self._get_outgoing_relationship(
            source_metric_id
        )

        if relationship.scenario_mapping is None:
            raise ValueError(
                f"No scenario mapping defined for relationship "
                f"'{relationship.source_metric_id}' -> "
                f"'{relationship.target_metric_id}'."
            )

        target_metric = self._get_metric(
            relationship.target_metric_id
        )

        target_scenario_value = propagate_metric_value(
            mapping=relationship.scenario_mapping,
            source_baseline=source_metric.current_value,
            source_value=source_scenario_value,
            target_baseline=target_metric.current_value,
        )

        return target_metric, target_scenario_value

    def propagate_path(
        self,
        source_metric_id: str,
        source_scenario_value: float,
        target_metric_id: str,
    ) -> list[tuple[Metric, float]]:
        """
        Propagate a scenario value through a causal path.

        Returns each downstream metric together with its scenario value.

        The path is discovered using the Value Graph relationships.
        """

        results: list[tuple[Metric, float]] = []

        current_metric_id = source_metric_id
        current_scenario_value = source_scenario_value

        visited: set[str] = set()

        while current_metric_id != target_metric_id:
            if current_metric_id in visited:
                raise ValueError(
                    f"Cycle detected while propagating from "
                    f"'{source_metric_id}'."
                )

            visited.add(current_metric_id)

            target_metric, target_scenario_value = self.propagate(
                source_metric_id=current_metric_id,
                source_scenario_value=current_scenario_value,
            )

            results.append(
                (target_metric, target_scenario_value)
            )

            current_metric_id = target_metric.id
            current_scenario_value = target_scenario_value

        return results

    def _get_metric(self, metric_id: str) -> Metric:
        for metric in self.graph.metrics:
            if metric.id == metric_id:
                return metric

        raise ValueError(
            f"Metric '{metric_id}' not found in Value Graph."
        )

    def _get_outgoing_relationship(self, metric_id: str):
        relationships = [
            relationship
            for relationship in self.graph.relationships
            if relationship.source_metric_id == metric_id
        ]

        if not relationships:
            raise ValueError(
                f"No outgoing relationship found for metric "
                f"'{metric_id}'."
            )

        if len(relationships) > 1:
            raise ValueError(
                f"Multiple outgoing relationships found for metric "
                f"'{metric_id}'."
            )

        return relationships[0]
