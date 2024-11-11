import enum
from typing import Annotated

import strawberry

from .account import Account


@strawberry.type
class AuthTokenPair:
    access_token: str
    refresh_token: str

