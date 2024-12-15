import strawberry

from eave.core.graphql.types.pricing import CostBreakdown


@strawberry.type
class TicketInfo:
    name: str | None
    notes: str | None
    cost_breakdown: CostBreakdown
