import strawberry

from eave.stdlib.typing import JsonObject


@strawberry.type
class CostBreakdown:
    min_base_cost_cents: int = 0
    base_cost_cents: int = 0
    fee_cents: int = 0
    tax_cents: int = 0

    @strawberry.field
    def total_cost_cents(self) -> int:
        return self.calculate_total_cost_cents()

    def calculate_total_cost_cents(self) -> int:
        # This is a function mostly for naming - I want the GraphQL field to be called `total_cost_cents`,
        # so if this was a property we'd have to call it something else, like `total_cost_cents_internal`,
        # which is an awkard name.
        return self.base_cost_cents + self.fee_cents + self.tax_cents

    def build_analytics_properties(self) -> JsonObject:
        # This is a function to make it clear to the caller that this returns a new dict every time.
        # If it was a property, the caller may think mutations to it will persist on this CostBreakdown instance.
        return {
            "total_cents": self.calculate_total_cost_cents(),
            "fees_cents": self.fee_cents,
            "tax_cents": self.tax_cents,
        }

    def __mul__(self, n: int) -> "CostBreakdown":
        return CostBreakdown(
            min_base_cost_cents=self.min_base_cost_cents * n,
            base_cost_cents=self.base_cost_cents * n,
            fee_cents=self.fee_cents * n,
            tax_cents=self.tax_cents * n,
        )

    def __add__(self, other: "CostBreakdown") -> "CostBreakdown":
        return CostBreakdown(
            min_base_cost_cents=self.min_base_cost_cents + other.min_base_cost_cents,
            base_cost_cents=self.base_cost_cents + other.base_cost_cents,
            fee_cents=self.fee_cents + other.fee_cents,
            tax_cents=self.tax_cents + other.tax_cents,
        )
