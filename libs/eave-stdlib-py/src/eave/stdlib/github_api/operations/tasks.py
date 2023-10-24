from typing import Unpack
import uuid
from eave.stdlib import requests
from eave.stdlib.api_types import BaseRequestBody, BaseResponseBody
from eave.stdlib.config import GITHUB_EVENT_QUEUE_NAME
from eave.stdlib.eave_origins import EaveApp

from eave.stdlib.github_api.models import GithubRepoInput
from eave.stdlib.github_api.operations import GithubAppEndpoint, GithubAppEndpointConfiguration
from eave.stdlib.headers import EAVE_REQUEST_ID_HEADER, EAVE_TEAM_ID_HEADER
from eave.stdlib.logging import LogContext
from eave.stdlib.task_queue import create_task


class RunApiDocumentationTask(GithubAppEndpoint):
    config = GithubAppEndpointConfiguration(
        path="/_/github/tasks/run-api-documentation",
    )

    class RequestBody(BaseRequestBody):
        repo: GithubRepoInput

    class ResponseBody(BaseResponseBody):
        pass

    @classmethod
    async def perform(
        cls, input: RequestBody, team_id: uuid.UUID, **kwargs: Unpack[requests.CommonRequestArgs]
    ) -> ResponseBody:
        return await requests.make_request(
            config=cls.config,
            response_type=cls.ResponseBody,
            input=input,
            team_id=team_id,
            **kwargs,
        )

    @classmethod
    async def perform_offline(cls, input: RequestBody, team_id: uuid.UUID, origin: EaveApp, ctx: LogContext) -> None:
        await create_task(
            ctx=ctx,
            audience=cls.config.audience,
            headers={
                EAVE_TEAM_ID_HEADER: str(team_id),
                EAVE_REQUEST_ID_HEADER: ctx.eave_request_id,
            },
            origin=origin,
            payload=input.json().encode(),
            queue_name=GITHUB_EVENT_QUEUE_NAME,
            target_path=cls.config.path,
        )
