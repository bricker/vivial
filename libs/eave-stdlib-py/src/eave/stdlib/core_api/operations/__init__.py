from dataclasses import dataclass
from typing import Mapping, Optional

from .. import models
from .base import Endpoint, EndpointConfiguration
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
    class ResponseBody(pydantic.BaseModel):
        service: str
        version: str
        status: str

class GetSubscription(Endpoint):
    config = EndpointConfiguration(
        path="/subscriptions/query",
        auth_required=False,
    )

    class RequestBody(pydantic.BaseModel):
        subscription: SubscriptionInput

    class ResponseBody(pydantic.BaseModel):
        team: models.Team
        subscription: models.Subscription
        document_reference: Optional[models.DocumentReference] = None


class CreateSubscription(Endpoint):
    config = EndpointConfiguration(
        path="/subscriptions/create",
        auth_required=False,
    )

    class RequestBody(pydantic.BaseModel):
        subscription: SubscriptionInput
        document_reference: Optional[DocumentReferenceInput] = None

    class ResponseBody(pydantic.BaseModel):
        team: models.Team
        subscription: models.Subscription
        document_reference: Optional[models.DocumentReference] = None


class DeleteSubscription(Endpoint):
    config = EndpointConfiguration(
        path="/subscriptions/delete",
        auth_required=False,
    )

    class RequestBody(pydantic.BaseModel):
        subscription: SubscriptionInput


class UpsertDocument(Endpoint):
    config = EndpointConfiguration(
        path="/documents/upsert",
        auth_required=False,
    )

    class RequestBody(pydantic.BaseModel):
        document: DocumentInput
        subscription: SubscriptionInput

    class ResponseBody(pydantic.BaseModel):
        team: models.Team
        subscription: models.Subscription
        document_reference: models.DocumentReference


class GetSlackInstallation(Endpoint):
    config = EndpointConfiguration(
        path="/integrations/slack/query",
        auth_required=False,
        team_id_required=False,
    )

    class RequestBody(pydantic.BaseModel):
        slack_integration: SlackInstallationInput

    class ResponseBody(pydantic.BaseModel):
        team: models.Team
        slack_integration: models.SlackInstallation


class GetGithubInstallation(Endpoint):
    config = EndpointConfiguration(
        path="/integrations/github/query",
        auth_required=False,
        team_id_required=False,
    )

    class RequestBody(pydantic.BaseModel):
        github_integration: GithubInstallationInput

    class ResponseBody(pydantic.BaseModel):
        team: models.Team
        github_integration: models.GithubInstallation




class GetAuthenticatedAccount(Endpoint):
    config = EndpointConfiguration(
        path="/me/query",
        team_id_required=False,
    )

    class ResponseBody(pydantic.BaseModel):
        account: models.AuthenticatedAccount
        team: models.Team


class GetAuthenticatedAccountTeamIntegrations(Endpoint):
    config = EndpointConfiguration(
        path="/me/team/integrations/query",
        team_id_required=False,
    )

    class ResponseBody(pydantic.BaseModel):
        account: models.AuthenticatedAccount
        team: models.Team
        integrations: models.Integrations


class GetTeam(Endpoint):
    config = EndpointConfiguration(
        path="/team/query",
        auth_required=False,
    )

    class ResponseBody(pydantic.BaseModel):
        team: models.Team
        integrations: models.Integrations
