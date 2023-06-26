from typing import Optional
import uuid
from eave.stdlib.core_api.operations.subscriptions import CreateSubscriptionRequest

from eave.stdlib.eave_origins import EaveOrigin
from eave.stdlib.logging import LogContext
from . import operations
from .. import requests
from ..config import shared_config


async def get_file_content(
    origin: EaveOrigin,
    eave_team_id: uuid.UUID,
    input: operations.GetGithubUrlContent.RequestBody,
    ctx: Optional[LogContext] = None,
) -> operations.GetGithubUrlContent.ResponseBody:
    """
    POST /github/api/content
    """
    response = await requests.make_request(
        url=f"{shared_config.eave_apps_base}/github/api/content",
        origin=origin,
        input=input,
        team_id=eave_team_id,
        ctx=ctx,
    )

    response_json = await response.json()
    return operations.GetGithubUrlContent.ResponseBody(**response_json)


async def create_subscription(
    origin: EaveOrigin,
    eave_team_id: uuid.UUID,
    input: operations.CreateGithubResourceSubscription.RequestBody,
    ctx: Optional[LogContext] = None,
) -> CreateSubscriptionRequest.ResponseBody:
    """
    POST /github/api/subscribe
    """
    response = await requests.make_request(
        url=f"{shared_config.eave_apps_base}/github/api/subscribe",
        origin=origin,
        input=input,
        team_id=eave_team_id,
        ctx=ctx,
    )

    response_json = await response.json()
    return CreateSubscriptionRequest.ResponseBody(**response_json)
