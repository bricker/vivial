import aiohttp
from typing import Optional
import pydantic
from eave.stdlib.config import shared_config


class EndpointConfiguration:
    path: str
    auth_required: bool
    team_id_required: bool
    signature_required: bool
    origin_required: bool

    def __init__(
        self,
        path: str,
        auth_required: bool = True,
        team_id_required: bool = True,
        signature_required: bool = True,
        origin_required: bool = True,
    ) -> None:
        self.path = path
        self.auth_required = auth_required
        self.team_id_required = team_id_required
        self.signature_required = signature_required
        self.origin_required = origin_required

    @property
    def url(self) -> str:
        return f"{shared_config.eave_api_base}{self.path}"


class BaseRequestBody(pydantic.BaseModel):
    pass


class BaseResponseBody(pydantic.BaseModel):
    _raw_response: Optional[aiohttp.ClientResponse] = None

    class Config:
        underscore_attrs_are_private = True


class Endpoint:
    pass
