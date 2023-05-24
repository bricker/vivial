from dataclasses import dataclass
from typing import Mapping, Optional
import aiohttp

from .. import models
from .base import BaseRequestBody, BaseResponseBody, Endpoint, EndpointConfiguration
from . import forge as forge
import pydantic

from .. import enums


class AccessTokenExchangeOfferInput(pydantic.BaseModel):
    auth_provider: enums.AuthProvider
    auth_id: str
    oauth_token: str


class DocumentInput(pydantic.BaseModel):
    title: str
    content: str
    parent: Optional["DocumentInput"] = None


class DocumentReferenceInput(pydantic.BaseModel):
    id: pydantic.UUID4


class SubscriptionInput(pydantic.BaseModel):
    source: models.SubscriptionSource


class TeamInput(pydantic.BaseModel):
    id: pydantic.UUID4


class SlackInstallationInput(pydantic.BaseModel):
    slack_team_id: str


class GithubInstallationInput(pydantic.BaseModel):
    github_install_id: str



class Status(Endpoint):
    class ResponseBody(BaseResponseBody):
        service: str
        version: str
        status: str

class GetSubscription(Endpoint):
    config = EndpointConfiguration(
        path="/subscriptions/query",
        auth_required=False,
    )

    class RequestBody(BaseRequestBody):
        subscription: SubscriptionInput

    class ResponseBody(BaseResponseBody):
        team: models.Team
        subscription: models.Subscription
        document_reference: Optional[models.DocumentReference] = None


class CreateSubscription(Endpoint):
    config = EndpointConfiguration(
        path="/subscriptions/create",
        auth_required=False,
    )

    class RequestBody(BaseRequestBody):
        subscription: SubscriptionInput
        document_reference: Optional[DocumentReferenceInput] = None

    class ResponseBody(BaseResponseBody):
        team: models.Team
        subscription: models.Subscription
        document_reference: Optional[models.DocumentReference] = None


class DeleteSubscription(Endpoint):
    config = EndpointConfiguration(
        path="/subscriptions/delete",
        auth_required=False,
    )

    class RequestBody(BaseRequestBody):
        subscription: SubscriptionInput


class UpsertDocument(Endpoint):
    config = EndpointConfiguration(
        path="/documents/upsert",
        auth_required=False,
    )

    class RequestBody(BaseRequestBody):
        document: DocumentInput
        subscriptions: list[SubscriptionInput]

    class ResponseBody(BaseResponseBody):
        team: models.Team
        subscriptions: list[models.Subscription]
        document_reference: models.DocumentReference


class SearchDocuments(Endpoint):
    config = EndpointConfiguration(
        path="/documents/search",
        auth_required=False,
    )

    class RequestBody(BaseRequestBody):
        query: str

    class ResponseBody(BaseResponseBody):
        team: models.Team
        documents: list[models.DocumentSearchResult]


class DeleteDocument(Endpoint):
    config = EndpointConfiguration(
        path="/documents/delete",
        auth_required=False,
    )

    class RequestBody(BaseRequestBody):
        document_reference: DocumentReferenceInput


class GetSlackInstallation(Endpoint):
    config = EndpointConfiguration(
        path="/integrations/slack/query",
        auth_required=False,
        team_id_required=False,
    )

    class RequestBody(BaseRequestBody):
        slack_integration: SlackInstallationInput

    class ResponseBody(BaseResponseBody):
        team: models.Team
        slack_integration: models.SlackInstallation


class GetGithubInstallation(Endpoint):
    config = EndpointConfiguration(
        path="/integrations/github/query",
        auth_required=False,
        team_id_required=False,
    )

    class RequestBody(BaseRequestBody):
        github_integration: GithubInstallationInput

    class ResponseBody(BaseResponseBody):
        team: models.Team
        github_integration: models.GithubInstallation


class GetAuthenticatedAccount(Endpoint):
    config = EndpointConfiguration(
        path="/me/query",
        team_id_required=False,
    )

    class ResponseBody(BaseResponseBody):
        account: models.AuthenticatedAccount
        team: models.Team


class GetAuthenticatedAccountTeamIntegrations(Endpoint):
    config = EndpointConfiguration(
        path="/me/team/integrations/query",
        team_id_required=False,
    )

    class ResponseBody(BaseResponseBody):
        account: models.AuthenticatedAccount
        team: models.Team
        integrations: models.Integrations


class GetTeam(Endpoint):
    config = EndpointConfiguration(
        path="/team/query",
        auth_required=False,
    )

    class ResponseBody(BaseResponseBody):
        team: models.Team
        integrations: models.Integrations
