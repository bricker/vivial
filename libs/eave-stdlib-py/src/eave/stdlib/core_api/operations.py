from typing import Optional
import aiohttp

import pydantic

from . import enums, models


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


class BaseResponseBody(pydantic.BaseModel):
    _raw_response: Optional[aiohttp.ClientResponse] = None

    class Config:
        underscore_attrs_are_private = True


class BaseRequestBody(pydantic.BaseModel):
    pass


class Status(Endpoint):
    class ResponseBody(BaseResponseBody):
        service: str
        version: str
        status: str


class CreateAccessRequest(Endpoint):
    class RequestBody(BaseRequestBody):
        visitor_id: Optional[pydantic.UUID4]
        email: pydantic.EmailStr
        opaque_input: str


class GetSubscription(Endpoint):
    class RequestBody(BaseRequestBody):
        subscription: SubscriptionInput

    class ResponseBody(BaseResponseBody):
        team: models.Team
        subscription: models.Subscription
        document_reference: Optional[models.DocumentReference] = None


class CreateSubscription(Endpoint):
    class RequestBody(BaseRequestBody):
        subscription: SubscriptionInput
        document_reference: Optional[DocumentReferenceInput] = None

    class ResponseBody(BaseResponseBody):
        team: models.Team
        subscription: models.Subscription
        document_reference: Optional[models.DocumentReference] = None


class DeleteSubscription(Endpoint):
    class RequestBody(BaseRequestBody):
        subscription: SubscriptionInput


class UpsertDocument(Endpoint):
    class RequestBody(BaseRequestBody):
        document: DocumentInput
        subscription: SubscriptionInput

    class ResponseBody(BaseResponseBody):
        team: models.Team
        subscription: models.Subscription
        document_reference: models.DocumentReference


class GetSlackInstallation(Endpoint):
    class RequestBody(BaseRequestBody):
        slack_integration: SlackInstallationInput

    class ResponseBody(BaseResponseBody):
        team: models.Team
        slack_integration: models.SlackInstallation


class GetGithubInstallation(Endpoint):
    class RequestBody(BaseRequestBody):
        github_integration: GithubInstallationInput

    class ResponseBody(BaseResponseBody):
        team: models.Team
        github_integration: models.GithubInstallation


class GetAtlassianInstallation(Endpoint):
    class RequestBody(BaseRequestBody):
        atlassian_integration: AtlassianInstallationInput

    class ResponseBody(BaseResponseBody):
        team: models.Team
        atlassian_integration: models.AtlassianInstallation


class UpdateAtlassianInstallation(Endpoint):
    class RequestBody(BaseRequestBody):
        atlassian_integration: UpdateAtlassianInstallationInput

    class ResponseBody(BaseResponseBody):
        account: models.AuthenticatedAccount
        team: models.Team
        atlassian_integration: models.AtlassianInstallation


class GetAuthenticatedAccount(Endpoint):
    class ResponseBody(BaseResponseBody):
        account: models.AuthenticatedAccount
        team: models.Team


class GetAuthenticatedAccountTeamIntegrations(Endpoint):
    class ResponseBody(BaseResponseBody):
        account: models.AuthenticatedAccount
        team: models.Team
        integrations: models.Integrations
        _raw_response: aiohttp.ClientResponse


class GetTeam(Endpoint):
    class ResponseBody(BaseResponseBody):
        team: models.Team
        integrations: models.Integrations
