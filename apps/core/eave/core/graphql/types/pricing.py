import strawberry


@strawberry.type
class Pricing:
    base_cost_cents: int = 0
    fee_cents: int = 0
    tax_cents: int = 0

    @strawberry.field
    def total_cost_cents(self) -> int:
        return self.total_cost_cents_internal

    @property
    def total_cost_cents_internal(self) -> int:
        return self.base_cost_cents + self.fee_cents + self.tax_cents
