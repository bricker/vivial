from uuid import UUID

import strawberry


@strawberry.type
class Outing:
    id: UUID
    visitor_id: str
    account_id: UUID | None
    survey_id: UUID
    # TODO: rest of the fields from ORM once that's finished
