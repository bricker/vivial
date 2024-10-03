
from eave.stdlib.core_api.models import BaseResponseModel


class AuthenticatedAccount(BaseResponseModel):
    email: str | None
