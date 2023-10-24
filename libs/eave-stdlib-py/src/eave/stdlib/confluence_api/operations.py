from typing import Unpack
import uuid

from eave.stdlib.api_types import BaseRequestBody, BaseResponseBody
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
from . import ConfluenceApiEndpoint, ConfluenceEndpointConfiguration


class GetAvailableSpacesRequest(ConfluenceApiEndpoint):
    config = ConfluenceEndpointConfiguration(
        path="/confluence/api/spaces/query",
    )

    class ResponseBody(BaseResponseBody):
        confluence_spaces: list[ConfluenceSpace]

    @classmethod
    async def perform(
        cls,
        team_id: uuid.UUID,
        **kwargs: Unpack[requests.CommonRequestArgs],
    ) -> ResponseBody:
        return await requests.make_request(
            config=cls.config,
            response_type=cls.ResponseBody,
            input=None,
            team_id=team_id,
            **kwargs,
        )


class SearchContentRequest(ConfluenceApiEndpoint):
    config = ConfluenceEndpointConfiguration(
        path="/confluence/api/content/search",
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
        return await requests.make_request(
            config=cls.config,
            response_type=cls.ResponseBody,
            input=input,
            team_id=team_id,
            **kwargs,
        )


class CreateContentRequest(ConfluenceApiEndpoint):
    config = ConfluenceEndpointConfiguration(
        path="/confluence/api/content/create",
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
        return await requests.make_request(
            config=cls.config,
            response_type=cls.ResponseBody,
            input=input,
            team_id=team_id,
            **kwargs,
        )


class UpdateContentRequest(ConfluenceApiEndpoint):
    config = ConfluenceEndpointConfiguration(
        path="/confluence/api/content/update",
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
        return await requests.make_request(
            config=cls.config,
            response_type=cls.ResponseBody,
            input=input,
            team_id=team_id,
            **kwargs,
        )


class DeleteContentRequest(ConfluenceApiEndpoint):
    config = ConfluenceEndpointConfiguration(
        path="/confluence/api/content/delete",
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
        return await requests.make_request(
            config=cls.config,
            response_type=cls.ResponseBody,
            input=input,
            team_id=team_id,
            **kwargs,
        )
