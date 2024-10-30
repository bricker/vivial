from datetime import datetime
from uuid import UUID

import strawberry


@strawberry.type
class Survey:
    id: UUID
    visitor_id: UUID
    start_time: datetime
    search_area_ids: list[str]
    budget: int
    headcount: int
