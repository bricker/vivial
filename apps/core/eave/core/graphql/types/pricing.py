import strawberry


@strawberry.type
class Pricing:
    base_cost_cents: int | None = 0
    fee_cents: int | None = 0
    tax_cents: int | None = 0
    total_cost_cents: int | None = 0
