import pydantic
from abc import abstractmethod
from http import HTTPMethod
from typing import Optional, Protocol

import aiohttp
from .eave_origins import EaveApp
from .config import shared_config


class BaseRequestBody(pydantic.BaseModel):
    pass


class BaseResponseBody(pydantic.BaseModel):
    _raw_response: Optional[aiohttp.ClientResponse] = None

    class Config:
        underscore_attrs_are_private = True

    @property
    def cookies(self) -> dict[str, str] | None:
        if self._raw_response:
            # SimpleCookie is a dict but invariant with dict[str,str], so convert it here
            return {k: v.value for k, v in self._raw_response.cookies.items()}
        else:
            return None


class ClientRequestParameters(Protocol):
    @property
    def path(self) -> str:
        ...

    @property
    def method(self) -> HTTPMethod:
        ...

    @property
    def audience(self) -> EaveApp:
        ...

    @property
    def base_url(self) -> str:
        return shared_config.eave_internal_service_base(self.audience)

    @property
    def url(self) -> str:
        return f"{self.base_url}{self.path}"


class ClientApiEndpointConfiguration(ClientRequestParameters):
    path: str
    method: HTTPMethod

    def __init__(self, path: str, method: HTTPMethod = HTTPMethod.POST) -> None:
        self.path = path
        self.method = method

    @property
    @abstractmethod
    def audience(self) -> EaveApp:
        ...


class ServerApiEndpointConfiguration(ClientRequestParameters):
    path: str
    method: HTTPMethod
    auth_required: bool
    team_id_required: bool
    signature_required: bool
    origin_required: bool

    @property
    @abstractmethod
    def audience(self) -> EaveApp:
        ...

    def __init__(
        self,
        path: str,
        method: HTTPMethod = HTTPMethod.POST,
        auth_required: bool = True,
        team_id_required: bool = True,
        signature_required: bool = True,
        origin_required: bool = True,
    ) -> None:
        self.path = path
        self.method = method
        self.auth_required = auth_required
        self.team_id_required = team_id_required
        self.signature_required = signature_required
        self.origin_required = origin_required


class GenericApiEndpointConfiguration(ClientRequestParameters):
    path: str
    method: HTTPMethod
    audience: EaveApp = EaveApp.eave_api

    def __init__(self, path: str, audience: EaveApp, method: HTTPMethod = HTTPMethod.POST) -> None:
        self.path = path
        self.method = method
        self.audience = audience
