from typing import Unpack
import uuid
from eave.stdlib.core_api.operations.subscriptions import CreateSubscriptionRequest

from eave.stdlib.eave_origins import EaveService
from . import operations
from .. import requests
from ..config import shared_config

_base_url = shared_config.eave_internal_service_base(EaveService.github)

async def get_file_content(
    eave_team_id: uuid.UUID,
    input: operations.GetGithubUrlContent.RequestBody,
    **kwargs: Unpack[requests.CommonRequestArgs],
) -> operations.GetGithubUrlContent.ResponseBody:
    """
    POST /github/api/content
    """
    response = await requests.make_request(
        url=f"{_base_url}/github/api/content",
        input=input,
        team_id=eave_team_id,
        **kwargs,
    )

    response_json = await response.json()
    return operations.GetGithubUrlContent.ResponseBody(**response_json)


async def create_subscription(
    eave_team_id: uuid.UUID,
    input: operations.CreateGithubResourceSubscription.RequestBody,
    **kwargs: Unpack[requests.CommonRequestArgs],
) -> CreateSubscriptionRequest.ResponseBody:
    """
    POST /github/api/subscribe
    """
    response = await requests.make_request(
        url=f"{_base_url}/github/api/subscribe",
        input=input,
        team_id=eave_team_id,
        **kwargs,
    )

    response_json = await response.json()
    return CreateSubscriptionRequest.ResponseBody(**response_json)
