import uuid
from . import operations
from ..lib.requests import make_request


async def get_file_content(
    eave_team_id: uuid.UUID,
    input: operations.GetGithubUrlContent.RequestBody,
) -> operations.GetGithubUrlContent.ResponseBody:
    """
    POST /github/content
    """
    response = await make_request(
        path="/github/content",
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
    POST /github/subscribe
    """
    response = await make_request(
        path="/github/subscribe",
        input=input,
        team_id=eave_team_id,
    )

    response_json = await response.json()
    return operations.CreateGithubResourceSubscription.ResponseBody(**response_json)
