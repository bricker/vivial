import enum
from typing import Annotated
from uuid import UUID

import strawberry


@strawberry.type
class Booking:
    id: UUID
    reserver_details_id: UUID
