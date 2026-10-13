from pydantic import BaseModel, Field


class AvailabilityRevenueInput(BaseModel):
    """
    Inputs required to calculate revenue recovered through
    improved transaction availability.
    """

    affected_transactions_per_month: float = Field(
        gt=0,
        description=(
            "Monthly transaction opportunity affected by "
            "the infrastructure issue."
        ),
    )

    recovery_rate: float = Field(
        ge=0,
        le=1,
        description=(
            "Fraction of affected transactions recovered "
            "through the improvement."
        ),
    )

    average_transaction_value: float = Field(
        gt=0,
        description="Average monetary value of one recovered transaction.",
    )

    months_per_year: int = Field(
        default=12,
        ge=1,
        le=12,
        description="Number of months used for annualization.",
    )


class AvailabilityRevenueResult(BaseModel):
    """
    Deterministic result produced by the Value Engine.
    """

    affected_transactions_per_month: float

    recovery_rate: float

    recovered_transactions_per_month: float

    average_transaction_value: float

    incremental_revenue_per_month: float

    incremental_revenue_per_year: float

    months_per_year: int
