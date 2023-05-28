import uuid
from uuid import UUID
import aiohttp

from eave.stdlib.core_api.operations.integrations import (
    GetAtlassianInstallation,
    GetGithubInstallation,
    GetSlackInstallation,
    UpdateAtlassianInstallation,
)

from .. import eave_origins as eave_origins
from . import operations
from .. import exceptions as eave_exceptions
from ..requests import make_request, makeurl

_ORIGIN: eave_origins.EaveOrigin


def set_origin(origin: eave_origins.EaveOrigin) -> None:
    global _ORIGIN
    _ORIGIN = origin


async def status() -> operations.Status.ResponseBody:
    async with aiohttp.ClientSession() as session:
        response = await session.request(
            "GET",
            makeurl("/status"),
        )

        response_json = await response.json()
    return operations.Status.ResponseBody(**response_json, _raw_response=response)


async def upsert_document(
    team_id: UUID,
    input: operations.UpsertDocument.RequestBody,
) -> operations.UpsertDocument.ResponseBody:
    response = await make_request(
        url=operations.UpsertDocument.config.url,
        input=input,
        team_id=team_id,
    )

    response_json = await response.json()
    return operations.UpsertDocument.ResponseBody(**response_json, _raw_response=response)


async def search_documents(
    team_id: UUID,
    input: operations.SearchDocuments.RequestBody,
) -> operations.SearchDocuments.ResponseBody:
    response = await make_request(
        url=operations.SearchDocuments.config.url,
        input=input,
        team_id=team_id,
    )

    response_json = await response.json()
    return operations.SearchDocuments.ResponseBody(**response_json, _raw_response=response)


async def delete_document(
    team_id: UUID,
    input: operations.DeleteDocument.RequestBody,
) -> operations.BaseResponseBody:
    response = await make_request(
        url=operations.DeleteDocument.config.url,
        input=input,
        team_id=team_id,
    )
    return operations.BaseResponseBody(_raw_response=response)


async def create_subscription(
    team_id: UUID,
    input: operations.CreateSubscription.RequestBody,
) -> operations.CreateSubscription.ResponseBody:
    response = await make_request(
        url=operations.CreateSubscription.config.url,
        input=input,
        team_id=team_id,
    )

    response_json = await response.json()
    return operations.CreateSubscription.ResponseBody(**response_json, _raw_response=response)


async def delete_subscription(
    team_id: UUID,
    input: operations.DeleteSubscription.RequestBody,
) -> operations.BaseResponseBody:
    response = await make_request(
        url=operations.DeleteSubscription.config.url,
        input=input,
        team_id=team_id,
    )

    return operations.BaseResponseBody(_raw_response=response)


async def get_subscription(
    team_id: UUID, input: operations.GetSubscription.RequestBody
) -> operations.GetSubscription.ResponseBody | None:
    try:
        response = await make_request(
            url=operations.GetSubscription.config.url,
            input=input,
            team_id=team_id,
        )
    except eave_exceptions.NotFoundError:
        # This operation is used to check for existing subscriptions, so a 404 is expected sometimes.
        return None

    response_json = await response.json()
    return operations.GetSubscription.ResponseBody(**response_json, _raw_response=response)


async def get_slack_installation(
    input: GetSlackInstallation.RequestBody,
) -> GetSlackInstallation.ResponseBody:
    response = await make_request(
        url=GetSlackInstallation.config.url,
        input=input,
    )

    response_json = await response.json()
    return GetSlackInstallation.ResponseBody(**response_json, _raw_response=response)


async def get_github_installation(
    input: GetGithubInstallation.RequestBody,
) -> GetGithubInstallation.ResponseBody:
    response = await make_request(
        url=GetGithubInstallation.config.url,
        input=input,
    )

    response_json = await response.json()
    return GetGithubInstallation.ResponseBody(**response_json, _raw_response=response)


async def get_atlassian_installation(
    input: GetAtlassianInstallation.RequestBody,
) -> GetAtlassianInstallation.ResponseBody:
    response = await make_request(
        url=GetAtlassianInstallation.config.url,
        input=input,
    )

    response_json = await response.json()
    return GetAtlassianInstallation.ResponseBody(**response_json, _raw_response=response)


async def get_team(
    team_id: UUID,
) -> operations.GetTeam.ResponseBody:
    response = await make_request(
        url=operations.GetTeam.config.url,
        input=None,
        team_id=team_id,
    )

    response_json = await response.json()
    return operations.GetTeam.ResponseBody(**response_json, _raw_response=response)


async def update_atlassian_integration(
    account_id: uuid.UUID,
    access_token: str,
    input: UpdateAtlassianInstallation.RequestBody,
) -> UpdateAtlassianInstallation.ResponseBody:
    response = await make_request(
        url=UpdateAtlassianInstallation.config.url,
        input=input,
        access_token=access_token,
        account_id=account_id,
    )

    response_json = await response.json()
    return UpdateAtlassianInstallation.ResponseBody(**response_json, _raw_response=response)


async def get_authenticated_account_team_integrations(
    account_id: UUID, access_token: str
) -> operations.GetAuthenticatedAccountTeamIntegrations.ResponseBody:
    response = await make_request(
        url=operations.GetAuthenticatedAccountTeamIntegrations.config.url,
        input=None,
        access_token=access_token,
        account_id=account_id,
    )

    response_json = await response.json()
    return operations.GetAuthenticatedAccountTeamIntegrations.ResponseBody(**response_json, _raw_response=response)


async def get_authenticated_account(
    account_id: UUID, access_token: str
) -> operations.GetAuthenticatedAccount.ResponseBody:
    response = await make_request(
        url=operations.GetAuthenticatedAccount.config.url,
        input=None,
        access_token=access_token,
        account_id=account_id,
    )

    response_json = await response.json()
    return operations.GetAuthenticatedAccount.ResponseBody(**response_json, _raw_response=response)
