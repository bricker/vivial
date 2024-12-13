import strawberry


@strawberry.type
class TicketInfo:
    name: str | None
    notes: str | None
