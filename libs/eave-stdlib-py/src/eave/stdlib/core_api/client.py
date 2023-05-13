import uuid
from uuid import UUID
import aiohttp

from .. import eave_origins as eave_origins
from . import operations
from .. import exceptions as eave_exceptions
from ..lib.requests import make_request, makeurl


async def status() -> operations.Status.ResponseBody:
    async with aiohttp.ClientSession() as session:
        response = await session.request(
            "GET",
            makeurl("/status"),
        )

    response_json = await response.json()
    return operations.Status.ResponseBody(**response_json, _raw_response=response)


async def create_access_request(
    input: operations.CreateAccessRequest.RequestBody,
) -> operations.BaseResponseBody:
    """
    POST /access_request
    """
    response = await make_request(
        path="/access_request",
        input=input,
    )

    return operations.BaseResponseBody(_raw_response=response)


async def upsert_document(
    team_id: UUID,
    input: operations.UpsertDocument.RequestBody,
) -> operations.UpsertDocument.ResponseBody:
    """
    POST /documents/upsert
    """
    response = await make_request(
        path="/documents/upsert",
        input=input,
        team_id=team_id,
    )

    response_json = await response.json()
    return operations.UpsertDocument.ResponseBody(**response_json, _raw_response=response)


async def create_subscription(
    team_id: UUID,
    input: operations.CreateSubscription.RequestBody,
) -> operations.CreateSubscription.ResponseBody:
    """
    POST /subscriptions/create
    """
    response = await make_request(
        path="/subscriptions/create",
        input=input,
        team_id=team_id,
    )

    response_json = await response.json()
    return operations.CreateSubscription.ResponseBody(**response_json, _raw_response=response)


async def delete_subscription(
    team_id: UUID,
    input: operations.DeleteSubscription.RequestBody,
) -> operations.BaseResponseBody:
    """
    POST /subscriptions/delete
    """
    response = await make_request(
        path="/subscriptions/delete",
        input=input,
        team_id=team_id,
    )

    return operations.BaseResponseBody(_raw_response=response)


async def get_subscription(
    team_id: UUID, input: operations.GetSubscription.RequestBody
) -> operations.GetSubscription.ResponseBody | None:
    """
    POST /subscriptions/query
    """
    try:
        response = await make_request(
            path="/subscriptions/query",
            input=input,
            team_id=team_id,
        )
    except eave_exceptions.NotFoundError:
        # This operation is used to check for existing subscriptions, so a 404 is expected sometimes.
        return None

    response_json = await response.json()
    return operations.GetSubscription.ResponseBody(**response_json, _raw_response=response)


async def get_slack_installation(
    input: operations.GetSlackInstallation.RequestBody,
) -> operations.GetSlackInstallation.ResponseBody:
    """
    POST /integrations/slack/query
    """
    response = await make_request(
        path="/integrations/slack/query",
        input=input,
    )

    response_json = await response.json()
    return operations.GetSlackInstallation.ResponseBody(**response_json, _raw_response=response)


async def get_github_installation(
    input: operations.GetGithubInstallation.RequestBody,
) -> operations.GetGithubInstallation.ResponseBody:
    """
    POST /integrations/github/query
    """
    response = await make_request(
        path="/integrations/github/query",
        input=input,
    )

    response_json = await response.json()
    return operations.GetGithubInstallation.ResponseBody(**response_json, _raw_response=response)


async def get_atlassian_installation(
    input: operations.GetAtlassianInstallation.RequestBody,
) -> operations.GetAtlassianInstallation.ResponseBody:
    """
    POST /integrations/atlassian/query
    """
    response = await make_request(
        path="/integrations/atlassian/query",
        input=input,
    )

    response_json = await response.json()
    return operations.GetAtlassianInstallation.ResponseBody(**response_json, _raw_response=response)


async def get_team(
    team_id: UUID,
) -> operations.GetTeam.ResponseBody:
    """
    POST /team/query
    """
    response = await make_request(
        path="/team/query",
        input=None,
        team_id=team_id,
    )

    response_json = await response.json()
    return operations.GetTeam.ResponseBody(**response_json, _raw_response=response)


async def update_atlassian_integration(
    account_id: uuid.UUID,
    access_token: str,
    input: operations.UpdateAtlassianInstallation.RequestBody,
) -> operations.UpdateAtlassianInstallation.ResponseBody:
    """
    POST /me/team/integrations/atlassian/update
    """
    response = await make_request(
        path="/me/team/integrations/atlassian/update",
        input=input,
        access_token=access_token,
        account_id=account_id,
    )

    response_json = await response.json()
    return operations.UpdateAtlassianInstallation.ResponseBody(**response_json, _raw_response=response)


async def get_authenticated_account_team_integrations(
    account_id: UUID, access_token: str
) -> operations.GetAuthenticatedAccountTeamIntegrations.ResponseBody:
    """
    POST /me/team/integrations/query
    """
    response = await make_request(
        path="/me/team/integrations/query",
        input=None,
        access_token=access_token,
        account_id=account_id,
    )

    response_json = await response.json()
    return operations.GetAuthenticatedAccountTeamIntegrations.ResponseBody(**response_json, _raw_response=response)


async def get_authenticated_account(
    account_id: UUID, access_token: str
) -> operations.GetAuthenticatedAccount.ResponseBody:
    """
    POST /me/query
    """
    response = await make_request(
        path="/me/query",
        input=None,
        access_token=access_token,
        account_id=account_id,
    )

    response_json = await response.json()
    return operations.GetAuthenticatedAccount.ResponseBody(**response_json, _raw_response=response)
