import aiohttp
from typing import Optional
import pydantic
from eave.stdlib.eave_origins import EaveService
from ...config import shared_config

_base_url = shared_config.eave_internal_service_base(EaveService.api)


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
        return f"{_base_url}{self.path}"


class BaseRequestBody(pydantic.BaseModel):
    pass


class BaseResponseBody(pydantic.BaseModel):
    _raw_response: Optional[aiohttp.ClientResponse] = None

    class Config:
        underscore_attrs_are_private = True


class Endpoint:
    config: EndpointConfiguration

    # @classmethod
    # async def perform(
    #     cls,
    #     origin: EaveOrigin,
    #     input: Optional[RequestBody] = None,
    #     team_id: Optional[uuid.UUID] = None,
    #     access_token: Optional[str] = None,
    #     account_id: Optional[uuid.UUID] = None,
    # ) -> ResponseBody:
    #     response = await requests.make_request(
    #         url=cls.config.url,
    #         origin=origin,
    #         input=input,
    #         team_id=team_id,
    #         access_token=access_token,
    #         account_id=account_id,
    #     )

    #     content_length = response.headers.get(aiohttp.hdrs.CONTENT_LENGTH)
    #     if content_length and int(content_length) > 0:
    #         response_json = await response.json()
    #         return cls.ResponseBody(**response_json, _raw_response=response)
    #     else:
    #         return cls.ResponseBody(_raw_response=response)
