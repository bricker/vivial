import uuid

from eave.stdlib.eave_origins import EaveOrigin
from . import operations
from .. import requests
from ..config import shared_config


async def get_file_content(
    origin: EaveOrigin,
    eave_team_id: uuid.UUID,
    input: operations.GetGithubUrlContent.RequestBody,
) -> operations.GetGithubUrlContent.ResponseBody:
    """
    POST /github/api/content
    """
    response = await requests.make_request(
        url=f"{shared_config.eave_apps_base}/github/api/content",
        origin=origin,
        input=input,
        team_id=eave_team_id,
    )

    response_json = await response.json()
    return operations.GetGithubUrlContent.ResponseBody(**response_json)


async def create_subscription(
    origin: EaveOrigin,
    eave_team_id: uuid.UUID,
    input: operations.CreateGithubResourceSubscription.RequestBody,
) -> operations.CreateGithubResourceSubscription.ResponseBody:
    """
    POST /github/api/subscribe
    """
    response = await requests.make_request(
        url=f"{shared_config.eave_apps_base}/github/api/subscribe",
        origin=origin,
        input=input,
        team_id=eave_team_id,
    )

    response_json = await response.json()
    return operations.CreateGithubResourceSubscription.ResponseBody(**response_json)
