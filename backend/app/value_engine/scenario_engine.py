from pathlib import Path

from app.repositories.value_graph_repository import ValueGraphRepository
from app.value_engine.availability_revenue import calculate_availability_revenue
from app.value_engine.models import AvailabilityRevenueInput
from app.value_engine.scenario_graph_propagator import (
    ScenarioGraphPropagator,
)
from app.value_engine.scenario_models import (
    Scenario,
    ScenarioMetricResult,
    ScenarioResult,
)


class ScenarioEngine:
    """
    Evaluates business-value scenarios against a customer's Value Graph.

    The engine validates scenario overrides, delegates causal propagation
    to ScenarioGraphPropagator, and uses deterministic value calculations
    for financial outcomes.
    """

    def __init__(self, data_root: Path):
        self.repository = ValueGraphRepository(data_root)

    def evaluate_scenario(
        self,
        customer_id: str,
        scenario: Scenario,
    ) -> ScenarioResult:
        graph = self.repository.load(customer_id)

        metric_results = []

        for override in scenario.overrides:
            metric = next(
                (
                    metric
                    for metric in graph.metrics
                    if metric.id == override.metric_id
                ),
                None,
            )

            if metric is None:
                raise ValueError(
                    f"Unknown metric '{override.metric_id}' "
                    f"for customer '{customer_id}'."
                )

            metric_results.append(
                ScenarioMetricResult(
                    metric_id=override.metric_id,
                    baseline_value=override.baseline_value,
                    scenario_value=override.scenario_value,
                    delta=override.scenario_value - override.baseline_value,
                )
            )

        baseline_annual_value = 0.0
        scenario_annual_value = 0.0

        propagator = ScenarioGraphPropagator(graph)

        for override in scenario.overrides:
            source_metric = next(
                metric
                for metric in graph.metrics
                if metric.id == override.metric_id
            )

            if override.baseline_value != source_metric.current_value:
                raise ValueError(
                    f"Scenario baseline {override.baseline_value} does not "
                    f"match graph baseline {source_metric.current_value} "
                    f"for metric '{override.metric_id}'."
                )

            relationships = [
                relationship
                for relationship in graph.relationships
                if relationship.source_metric_id == override.metric_id
            ]

            if not relationships:
                continue

            recovery_relationship = relationships[0]

            if recovery_relationship.scenario_mapping is None:
                raise ValueError(
                    f"No scenario mapping defined for relationship "
                    f"'{recovery_relationship.source_metric_id}' -> "
                    f"'{recovery_relationship.target_metric_id}'."
                )

            first_target_metric, scenario_recovery_rate = propagator.propagate(
                source_metric_id=override.metric_id,
                source_scenario_value=override.scenario_value,
            )

            baseline_recovery_rate = first_target_metric.current_value

            if first_target_metric.layer != "technical_kpi":
                continue

            downstream_results = propagator.propagate_path(
                source_metric_id=first_target_metric.id,
                source_scenario_value=scenario_recovery_rate,
                target_metric_id="incremental_revenue",
            )

            if not downstream_results:
                continue

            recovered_transactions_metric, scenario_recovered_transactions = (
                downstream_results[0]
            )

            revenue_metric, scenario_revenue = downstream_results[-1]

            if recovered_transactions_metric.id != "recovered_transactions":
                raise ValueError(
                    "Expected recovered transactions in the value path."
                )

            if revenue_metric.id != "incremental_revenue":
                raise ValueError(
                    "Expected incremental revenue in the value path."
                )

            affected_transactions_relationship = next(
                (
                    relationship
                    for relationship in graph.relationships
                    if (
                        relationship.target_metric_id
                        == recovered_transactions_metric.id
                    )
                ),
                None,
            )

            if affected_transactions_relationship is None:
                raise ValueError(
                    f"No relationship found for target metric "
                    f"'{recovered_transactions_metric.id}'."
                )

            affected_transactions_per_month = (
                affected_transactions_relationship.coefficient
            )

            if affected_transactions_per_month <= 0:
                raise ValueError(
                    "Affected transactions per month must be positive."
                )

            revenue_relationship = next(
                (
                    relationship
                    for relationship in graph.relationships
                    if (
                        relationship.source_metric_id
                        == recovered_transactions_metric.id
                        and relationship.target_metric_id
                        == revenue_metric.id
                    )
                ),
                None,
            )

            if revenue_relationship is None:
                raise ValueError(
                    f"No relationship found from "
                    f"'{recovered_transactions_metric.id}' to "
                    f"'{revenue_metric.id}'."
                )

            average_transaction_value = revenue_relationship.coefficient

            if average_transaction_value <= 0:
                raise ValueError(
                    "Average transaction value must be positive."
                )

            baseline_result = calculate_availability_revenue(
                AvailabilityRevenueInput(
                    affected_transactions_per_month=affected_transactions_per_month,
                    recovery_rate=baseline_recovery_rate,
                    average_transaction_value=average_transaction_value,
                )
            )

            scenario_result = calculate_availability_revenue(
                AvailabilityRevenueInput(
                    affected_transactions_per_month=affected_transactions_per_month,
                    recovery_rate=scenario_recovery_rate,
                    average_transaction_value=average_transaction_value,
                )
            )

            baseline_annual_value = (
                baseline_result.incremental_revenue_per_year
            )

            scenario_annual_value = (
                scenario_result.incremental_revenue_per_year
            )

        return ScenarioResult(
            scenario_id=scenario.scenario_id,
            scenario_name=scenario.name,
            metric_results=metric_results,
            baseline_annual_value=baseline_annual_value,
            scenario_annual_value=scenario_annual_value,
            annual_value_delta=(
                scenario_annual_value - baseline_annual_value
            ),
        )
