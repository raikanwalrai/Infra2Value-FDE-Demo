from pathlib import Path

import pytest

from app.repositories.value_graph_repository import (
    ValueGraphRepository,
)
from app.value_engine.impact_engine import (
    ValueImpactEngine,
)


DATA_ROOT = Path(__file__).resolve().parents[2] / "data"


@pytest.fixture
def engine():
    repository = ValueGraphRepository(DATA_ROOT)
    return ValueImpactEngine(repository)


def test_starbucks_network_to_ceo_impact(engine):
    result = engine.calculate_impact(
        customer_id="starbucks",
        source_metric_id="network_availability",
        target_metric_id="ceo_revenue_growth",
    )

    assert result.metric_path == [
        "network_availability",
        "digital_transaction_recovery",
        "recovered_transactions",
        "incremental_revenue",
        "ceo_revenue_growth",
    ]

    assert result.recovered_transactions_per_month == pytest.approx(
        1600
    )

    assert result.incremental_revenue_per_month == pytest.approx(
        12800
    )

    assert result.incremental_revenue_per_year == pytest.approx(
        153600
    )


def test_impact_result_contains_relationship_evidence(engine):
    result = engine.calculate_impact(
        customer_id="starbucks",
        source_metric_id="network_availability",
        target_metric_id="ceo_revenue_growth",
    )

    assert len(result.impact_steps) == 4

    assert result.impact_steps[0].relationship_type == "causes"

    assert result.impact_steps[0].coefficient == pytest.approx(
        0.4
    )

    assert result.impact_steps[2].coefficient == pytest.approx(
        8
    )


def test_invalid_impact_path_raises_error(engine):
    with pytest.raises(ValueError):
        engine.calculate_impact(
            customer_id="starbucks",
            source_metric_id="network_availability",
            target_metric_id="nonexistent_metric",
        )
