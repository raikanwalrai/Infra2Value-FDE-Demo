from app.models.value_graph import ScenarioMapping


def calculate_target_delta(
    mapping: ScenarioMapping,
    source_baseline: float,
    source_value: float,
    target_baseline: float,
) -> float:
    """
    Calculate the change in a target metric produced by a scenario.

    Mapping semantics:

    target_based:
        target delta = configured target value - target baseline

    proportional:
        target delta =
            (source scenario value - source baseline) * coefficient

    The returned value is always a DELTA, not the final target value.
    """

    if mapping.type == "target_based":
        return mapping.target_value - target_baseline

    if mapping.type == "proportional":
        source_delta = source_value - source_baseline
        return source_delta * mapping.target_value

    raise ValueError(
        f"Unsupported scenario mapping type '{mapping.type}'."
    )
