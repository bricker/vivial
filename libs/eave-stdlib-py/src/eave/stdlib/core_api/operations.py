from typing import Optional, Sequence

import eave.stdlib.core_api.enums
import pydantic

from . import models


class AccessTokenExchangeOfferInput(pydantic.BaseModel):
    auth_provider: eave.stdlib.core_api.enums.AuthProvider
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
    confluence_space: Optional[str]


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


class GetSubscriptions(Endpoint):
    class RequestBody(pydantic.BaseModel):
        subscription: SubscriptionInput
        document_reference: Optional[DocumentReferenceInput] = None

    class ResponseBody(pydantic.BaseModel):
        """
        `subscriptions` and `document_references` have the same length
        and each index corresponds directly.
        e.g. `subscriptions[1].document_reference_id == document_references[1].id`
        `document_references` has None entries where the corresponding Subscription
        has a None document_reference_id.
        """

        team: models.Team
        subscriptions: Sequence[models.Subscription]
        document_references: Sequence[Optional[models.DocumentReference]]


class CreateSubscription(Endpoint):
    class RequestBody(pydantic.BaseModel):
        subscription: SubscriptionInput
        document_reference: Optional[DocumentReferenceInput] = None

    class ResponseBody(pydantic.BaseModel):
        team: models.Team
        subscription: models.Subscription
        document_reference: Optional[models.DocumentReference] = None


class DeleteSubscriptions(Endpoint):
    class RequestBody(pydantic.BaseModel):
        subscription: SubscriptionInput
        document_reference: Optional[DocumentReferenceInput] = None


class UpsertDocument(Endpoint):
    class RequestBody(pydantic.BaseModel):
        document: DocumentInput
        subscriptions: Sequence[models.Subscription]

    class ResponseBody(pydantic.BaseModel):
        team: models.Team
        subscriptions: Sequence[models.Subscription]
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
