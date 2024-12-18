import strawberry


@strawberry.type
class CostBreakdown:
    base_cost_cents: int = 0
    fee_cents: int = 0
    tax_cents: int = 0

    @strawberry.field
    def total_cost_cents(self) -> int:
        return self.total_cost_cents_internal

    @property
    def total_cost_cents_internal(self) -> int:
        return self.base_cost_cents + self.fee_cents + self.tax_cents

    def __mul__(self, n: int) -> "CostBreakdown":
        return CostBreakdown(
            base_cost_cents=self.base_cost_cents * n,
            fee_cents=self.fee_cents * n,
            tax_cents=self.tax_cents * n,
        )

    def __add__(self, other: "CostBreakdown") -> "CostBreakdown":
        return CostBreakdown(
            base_cost_cents=self.base_cost_cents + other.base_cost_cents,
            fee_cents=self.fee_cents + other.fee_cents,
            tax_cents=self.tax_cents + other.tax_cents,
        )
