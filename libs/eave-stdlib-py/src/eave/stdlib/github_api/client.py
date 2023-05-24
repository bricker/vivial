import uuid
from . import operations
from ..requests import make_request
from ..config import shared_config


async def get_file_content(
    eave_team_id: uuid.UUID,
    input: operations.GetGithubUrlContent.RequestBody,
) -> operations.GetGithubUrlContent.ResponseBody:
    """
    POST /github/api/content
    """
    response = await make_request(
        url=f"{shared_config.eave_apps_base}/github/api/content",
        input=input,
        team_id=eave_team_id,
    )

    response_json = await response.json()
    return operations.GetGithubUrlContent.ResponseBody(**response_json)


async def create_subscription(
    eave_team_id: uuid.UUID,
    input: operations.CreateGithubResourceSubscription.RequestBody,
) -> operations.CreateGithubResourceSubscription.ResponseBody:
    """
    POST /github/api/subscribe
    """
    response = await make_request(
        url=f"{shared_config.eave_apps_base}/github/api/subscribe",
        input=input,
        team_id=eave_team_id,
    )

    response_json = await response.json()
    return operations.CreateGithubResourceSubscription.ResponseBody(**response_json)
