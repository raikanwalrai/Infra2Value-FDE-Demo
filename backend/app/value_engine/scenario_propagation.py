from app.models.value_graph import ScenarioMapping
from app.value_engine.scenario_mapping import calculate_target_delta


def propagate_metric_value(
    mapping: ScenarioMapping,
    source_baseline: float,
    source_value: float,
    target_baseline: float,
) -> float:
    """
    Calculate the final target metric value produced by a scenario.

    The lower-level scenario mapping function calculates the target DELTA.
    This function converts that delta into the final target scenario value.
    """

    target_delta = calculate_target_delta(
        mapping=mapping,
        source_baseline=source_baseline,
        source_value=source_value,
        target_baseline=target_baseline,
    )

    return target_baseline + target_delta
