from typing import Generic, Optional, Type, TypeVar

import aiohttp
import eave.stdlib.core_api.operations.status as status
import pydantic
from eave.stdlib.eave_origins import EaveApp

from .config import SHARED_CONFIG


def status_payload() -> status.Status.ResponseBody:
    return status.Status.ResponseBody(
        service=SHARED_CONFIG.app_service,
        version=SHARED_CONFIG.app_version,
        status="OK",
    )


class EndpointConfiguration:
    base_url: str
    path: str
    audience: EaveApp
    method: str
    auth_required: bool
    team_id_required: bool
    signature_required: bool
    origin_required: bool

    def __init__(
        self,
        *,
        base_url: str,
        path: str,
        audience: EaveApp,
        method: str,
        auth_required: bool,
        team_id_required: bool,
        signature_required: bool,
        origin_required: bool,
    ) -> None:
        self.base_url = base_url
        self.path = path
        self.audience = audience
        self.method = method
        self.auth_required = auth_required
        self.team_id_required = team_id_required
        self.signature_required = signature_required
        self.origin_required = origin_required

    @property
    def url(self) -> str:
        return f"{self.base_url}{self.path}"


class BaseRequestBody(pydantic.BaseModel):
    pass


class BaseResponseBody(pydantic.BaseModel):
    raw_response: Optional[aiohttp.ClientResponse] = None

    class Config:
        underscore_attrs_are_private = True

    @property
    def cookies(self) -> dict[str, str] | None:
        if self.raw_response:
            # SimpleCookie is a dict but invariant with dict[str,str], so convert it here
            return {k: v.value for k, v in self.raw_response.cookies.items()}
        else:
            return None


_SomeResponseBody = TypeVar("_SomeResponseBody", bound=BaseResponseBody)
_SomeEndpointConfiguration = TypeVar("_SomeEndpointConfiguration", bound=EndpointConfiguration)


class Endpoint(Generic[_SomeEndpointConfiguration]):
    config: _SomeEndpointConfiguration

    @classmethod
    async def make_response(
        cls, response: aiohttp.ClientResponse, response_type: Type[_SomeResponseBody]
    ) -> _SomeResponseBody:
        response_json = await response.json()
        if response_json:
            r = response_type(**response_json)
        else:
            r = response_type()
        r.raw_response = response
        return r
