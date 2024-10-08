from typing import Optional
from uuid import UUID

import strawberry

@strawberry.type
class Account:
    id: UUID = strawberry.field()
    email: str = strawberry.field()
