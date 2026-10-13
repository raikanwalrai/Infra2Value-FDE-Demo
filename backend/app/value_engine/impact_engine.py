from app.repositories.value_graph_repository import (
    ValueGraphRepository,
)
from app.graph.value_graph_traversal import ValueGraphTraversal

from .availability_revenue import (
    calculate_availability_revenue,
)
from .impact_models import (
    ImpactStep,
    ValueImpactResult,
)
from .models import AvailabilityRevenueInput


class ValueImpactEngine:
    """
    Integrates the Value Graph with deterministic Value Engine
    calculations.

    The repository provides the customer Value Graph.

    The graph determines:
        - what causes what
        - coefficients
        - assumptions
        - confidence

    The Value Engine determines:
        - recovered transactions
        - monthly revenue
        - annual revenue
    """

    def __init__(
        self,
        repository: ValueGraphRepository,
    ):
        self.repository = repository

    def calculate_impact(
        self,
        customer_id: str,
        source_metric_id: str,
        target_metric_id: str,
    ) -> ValueImpactResult:

        graph = self.repository.load(customer_id)

        traversal = ValueGraphTraversal(graph)

        try:
            metric_path = traversal.find_impact_path(
                source_metric_id,
                target_metric_id,
            )
        except KeyError as exc:
            raise ValueError(str(exc)) from exc

        if not metric_path:
            raise ValueError(
                f"No impact path found from "
                f"{source_metric_id} to {target_metric_id}"
            )

        metric_path_ids = [
            metric.id
            for metric in metric_path
        ]

        relationships = traversal.get_relationships_for_path(
            metric_path
        )

        impact_steps = [
            ImpactStep(
                source_metric_id=relationship.source_metric_id,
                target_metric_id=relationship.target_metric_id,
                relationship_type=relationship.relationship_type,
                coefficient=relationship.coefficient,
                assumption=relationship.assumption,
                confidence=relationship.confidence,
            )
            for relationship in relationships
        ]

        affected_transactions = self._get_affected_transactions(
            relationships
        )

        recovery_rate = self._get_recovery_rate(
            relationships
        )

        average_transaction_value = (
            self._get_average_transaction_value(
                relationships
            )
        )

        calculation = calculate_availability_revenue(
            AvailabilityRevenueInput(
                affected_transactions_per_month=affected_transactions,
                recovery_rate=recovery_rate,
                average_transaction_value=average_transaction_value,
            )
        )

        return ValueImpactResult(
            customer_id=customer_id,
            source_metric_id=source_metric_id,
            target_metric_id=target_metric_id,
            metric_path=metric_path_ids,
            impact_steps=impact_steps,
            recovered_transactions_per_month=(
                calculation.recovered_transactions_per_month
            ),
            incremental_revenue_per_month=(
                calculation.incremental_revenue_per_month
            ),
            incremental_revenue_per_year=(
                calculation.incremental_revenue_per_year
            ),
        )

    @staticmethod
    def _get_recovery_rate(relationships):
        for relationship in relationships:
            if relationship.target_metric_id == (
                "digital_transaction_recovery"
            ):
                return relationship.coefficient

        raise ValueError(
            "Recovery rate assumption not found in Value Graph."
        )

    @staticmethod
    def _get_affected_transactions(relationships):
        for relationship in relationships:
            if relationship.target_metric_id == (
                "recovered_transactions"
            ):
                return relationship.coefficient

        raise ValueError(
            "Affected transaction assumption not found "
            "in Value Graph."
        )

    @staticmethod
    def _get_average_transaction_value(relationships):
        for relationship in relationships:
            if relationship.target_metric_id == (
                "incremental_revenue"
            ):
                return relationship.coefficient

        raise ValueError(
            "Average transaction value assumption not found "
            "in Value Graph."
        )
