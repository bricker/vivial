from typing import Optional

import pydantic

from . import models
from . import enums

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


class AtlassianInstallationInput(pydantic.BaseModel):
    atlassian_cloud_id: str

class UpdateAtlassianInstallationInput(pydantic.BaseModel):
    confluence_space_key: Optional[str]


class Endpoint:
    pass


class Status(Endpoint):
    class ResponseBody(pydantic.BaseModel):
        service: str
        version: str
        status: str


class CreateAccessRequest(Endpoint):
    class RequestBody(pydantic.BaseModel):
        visitor_id: Optional[pydantic.UUID4]
        email: pydantic.EmailStr
        opaque_input: str


class GetSubscription(Endpoint):
    class RequestBody(pydantic.BaseModel):
        subscription: SubscriptionInput

    class ResponseBody(pydantic.BaseModel):
        team: models.Team
        subscription: models.Subscription
        document_reference: Optional[models.DocumentReference] = None


class CreateSubscription(Endpoint):
    class RequestBody(pydantic.BaseModel):
        subscription: SubscriptionInput
        document_reference: Optional[DocumentReferenceInput] = None

    class ResponseBody(pydantic.BaseModel):
        team: models.Team
        subscription: models.Subscription
        document_reference: Optional[models.DocumentReference] = None


class DeleteSubscription(Endpoint):
    class RequestBody(pydantic.BaseModel):
        subscription: SubscriptionInput


class UpsertDocument(Endpoint):
    class RequestBody(pydantic.BaseModel):
        document: DocumentInput
        subscription: SubscriptionInput

    class ResponseBody(pydantic.BaseModel):
        team: models.Team
        subscription: models.Subscription
        document_reference: models.DocumentReference


class GetSlackInstallation(Endpoint):
    class RequestBody(pydantic.BaseModel):
        slack_integration: SlackInstallationInput

    class ResponseBody(pydantic.BaseModel):
        team: models.Team
        slack_integration: models.SlackInstallation


class GetGithubInstallation(Endpoint):
    class RequestBody(pydantic.BaseModel):
        github_integration: GithubInstallationInput

    class ResponseBody(pydantic.BaseModel):
        team: models.Team
        github_integration: models.GithubInstallation


class GetAtlassianInstallation(Endpoint):
    class RequestBody(pydantic.BaseModel):
        atlassian_integration: AtlassianInstallationInput

    class ResponseBody(pydantic.BaseModel):
        team: models.Team
        atlassian_integration: models.AtlassianInstallation

class UpdateAtlassianInstallation(Endpoint):
    class RequestBody(pydantic.BaseModel):
        atlassian_integration: UpdateAtlassianInstallationInput

    class ResponseBody(pydantic.BaseModel):
        account: models.AuthenticatedAccount
        team: models.Team
        atlassian_integration: models.AtlassianInstallation


class GetAuthenticatedAccount(Endpoint):
    class ResponseBody(pydantic.BaseModel):
        account: models.AuthenticatedAccount
        team: models.Team


class GetAuthenticatedAccountTeamIntegrations(Endpoint):
    class ResponseBody(pydantic.BaseModel):
        account: models.AuthenticatedAccount
        team: models.Team
        integrations: models.Integrations


class GetTeam(Endpoint):
    class ResponseBody(pydantic.BaseModel):
        team: models.Team
        integrations: models.Integrations
