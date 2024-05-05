from typing import Generic, TypeVar

import aiohttp
import pydantic

from eave.stdlib.eave_origins import EaveApp


class EndpointConfiguration:
    base_url: str
    path: str
    audience: EaveApp
    method: str
    auth_required: bool
    origin_required: bool
    is_public: bool

    def __init__(
        self,
        *,
        base_url: str,
        path: str,
        audience: EaveApp,
        method: str,
        auth_required: bool,
        origin_required: bool,
        is_public: bool = False,
    ) -> None:
        self.base_url = base_url
        self.path = path
        self.audience = audience
        self.method = method
        self.auth_required = auth_required
        self.origin_required = origin_required
        self.is_public = is_public

    @property
    def url(self) -> str:
        return f"{self.base_url}{self.path}"


class BaseRequestBody(pydantic.BaseModel):
    pass


class BaseResponseBody(pydantic.BaseModel):
    _raw_response: aiohttp.ClientResponse | None = None

    class Config:
        underscore_attrs_are_private = True

    @property
    def raw_response(self) -> aiohttp.ClientResponse | None:
        return self._raw_response

    def set_raw_response(self, value: aiohttp.ClientResponse | None) -> None:
        """
        This isn't a proper setter function because Pydantic hijacks attr lookups.
        Calling `resp.raw_response = x` throws an error that there isn't a `raw_response` field.
        """
        self._raw_response = value

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
        cls, response: aiohttp.ClientResponse, response_type: type[_SomeResponseBody]
    ) -> _SomeResponseBody:
        response_json = await response.json()
        if response_json:
            r = response_type(**response_json)
        else:
            r = response_type()
        r.set_raw_response(response)
        return r
