import pytest

from app.value_engine.availability_revenue import (
    calculate_availability_revenue,
)
from app.value_engine.models import AvailabilityRevenueInput


def test_availability_revenue_calculation():
    inputs = AvailabilityRevenueInput(
        affected_transactions_per_month=4000,
        recovery_rate=0.40,
        average_transaction_value=8,
    )

    result = calculate_availability_revenue(inputs)

    assert result.recovered_transactions_per_month == pytest.approx(
        1600
    )

    assert result.incremental_revenue_per_month == pytest.approx(
        12800
    )

    assert result.incremental_revenue_per_year == pytest.approx(
        153600
    )


def test_zero_recovery_produces_zero_value():
    inputs = AvailabilityRevenueInput(
        affected_transactions_per_month=4000,
        recovery_rate=0,
        average_transaction_value=8,
    )

    result = calculate_availability_revenue(inputs)

    assert result.recovered_transactions_per_month == 0
    assert result.incremental_revenue_per_month == 0
    assert result.incremental_revenue_per_year == 0


def test_custom_annualization_period():
    inputs = AvailabilityRevenueInput(
        affected_transactions_per_month=1000,
        recovery_rate=0.10,
        average_transaction_value=20,
        months_per_year=6,
    )

    result = calculate_availability_revenue(inputs)

    assert result.recovered_transactions_per_month == pytest.approx(
        100
    )

    assert result.incremental_revenue_per_month == pytest.approx(
        2000
    )

    assert result.incremental_revenue_per_year == pytest.approx(
        12000
    )
