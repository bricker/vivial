from typing import Unpack
import uuid
from .. import requests
from eave.stdlib.confluence_api.models import (
    ConfluenceSearchParamsInput,
    ConfluenceSearchResultWithBody,
    DeleteContentInput,
    UpdateContentInput,
)
from eave.stdlib.confluence_api.models import ConfluencePage, ConfluenceSpace
from eave.stdlib.core_api.models.team import ConfluenceDestinationInput
from eave.stdlib.core_api.models.documents import DocumentInput
from eave.stdlib.core_api.operations import BaseRequestBody, BaseResponseBody
from . import ConfluenceEndpoint, ConfluenceEndpointConfiguration


class GetAvailableSpacesRequest(ConfluenceEndpoint):
    config = ConfluenceEndpointConfiguration(
        path="/spaces/query",
        auth_required=False,
    )

    class ResponseBody(BaseResponseBody):
        confluence_spaces: list[ConfluenceSpace]

    @classmethod
    async def perform(
        cls,
        team_id: uuid.UUID,
        **kwargs: Unpack[requests.CommonRequestArgs],
    ) -> ResponseBody:
        response = await requests.make_request(
            config=cls.config,
            input=None,
            team_id=team_id,
            **kwargs,
        )

        response_json = await response.json()
        return cls.ResponseBody(**response_json, _raw_response=response)


class SearchContentRequest(ConfluenceEndpoint):
    config = ConfluenceEndpointConfiguration(
        path="/content/search",
        auth_required=False,
    )

    class RequestBody(BaseRequestBody):
        search_params: ConfluenceSearchParamsInput

    class ResponseBody(BaseResponseBody):
        results: list[ConfluenceSearchResultWithBody]

    @classmethod
    async def perform(
        cls,
        team_id: uuid.UUID,
        input: RequestBody,
        **kwargs: Unpack[requests.CommonRequestArgs],
    ) -> ResponseBody:
        response = await requests.make_request(
            config=cls.config,
            input=input,
            team_id=team_id,
            **kwargs,
        )

        response_json = await response.json()
        return cls.ResponseBody(**response_json, _raw_response=response)


class CreateContentRequest(ConfluenceEndpoint):
    config = ConfluenceEndpointConfiguration(
        path="/content/create",
        auth_required=False,
    )

    class RequestBody(BaseRequestBody):
        confluence_destination: ConfluenceDestinationInput
        document: DocumentInput

    class ResponseBody(BaseResponseBody):
        content: ConfluencePage

    @classmethod
    async def perform(
        cls,
        team_id: uuid.UUID,
        input: RequestBody,
        **kwargs: Unpack[requests.CommonRequestArgs],
    ) -> ResponseBody:
        response = await requests.make_request(
            config=cls.config,
            input=input,
            team_id=team_id,
            **kwargs,
        )

        response_json = await response.json()
        return cls.ResponseBody(**response_json, _raw_response=response)


class UpdateContentRequest(ConfluenceEndpoint):
    config = ConfluenceEndpointConfiguration(
        path="/content/update",
        auth_required=False,
    )

    class RequestBody(BaseRequestBody):
        content: UpdateContentInput

    class ResponseBody(BaseResponseBody):
        content: ConfluencePage

    @classmethod
    async def perform(
        cls,
        team_id: uuid.UUID,
        input: RequestBody,
        **kwargs: Unpack[requests.CommonRequestArgs],
    ) -> ResponseBody:
        response = await requests.make_request(
            config=cls.config,
            input=input,
            team_id=team_id,
            **kwargs,
        )

        response_json = await response.json()
        return cls.ResponseBody(**response_json, _raw_response=response)


class DeleteContentRequest(ConfluenceEndpoint):
    config = ConfluenceEndpointConfiguration(
        path="/content/delete",
        auth_required=False,
    )

    class RequestBody(BaseRequestBody):
        content: DeleteContentInput

    class ResponseBody(BaseResponseBody):
        pass

    @classmethod
    async def perform(
        cls,
        team_id: uuid.UUID,
        input: RequestBody,
        **kwargs: Unpack[requests.CommonRequestArgs],
    ) -> ResponseBody:
        response = await requests.make_request(
            config=cls.config,
            input=input,
            team_id=team_id,
            **kwargs,
        )

        return cls.ResponseBody(_raw_response=response)
