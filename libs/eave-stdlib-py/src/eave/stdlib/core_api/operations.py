from typing import Optional

import pydantic

from . import models

class AccessTokenExchangeOfferInput(pydantic.BaseModel):
    auth_provider: models.AuthProvider
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


class Status:
    class ResponseBody(pydantic.BaseModel):
        service: str
        version: str
        status: str


class CreateAccessRequest:
    class RequestBody(pydantic.BaseModel):
        visitor_id: Optional[pydantic.UUID4]
        email: pydantic.EmailStr
        opaque_input: str


class GetSubscription:
    class RequestBody(pydantic.BaseModel):
        subscription: SubscriptionInput

    class ResponseBody(pydantic.BaseModel):
        team: models.Team
        subscription: models.Subscription
        document_reference: Optional[models.DocumentReference] = None


class CreateSubscription:
    class RequestBody(pydantic.BaseModel):
        subscription: SubscriptionInput
        document_reference: Optional[DocumentReferenceInput] = None

    class ResponseBody(pydantic.BaseModel):
        team: models.Team
        subscription: models.Subscription
        document_reference: Optional[models.DocumentReference] = None


class DeleteSubscription:
    class RequestBody(pydantic.BaseModel):
        subscription: SubscriptionInput


class UpsertDocument:
    class RequestBody(pydantic.BaseModel):
        document: DocumentInput
        subscription: SubscriptionInput

    class ResponseBody(pydantic.BaseModel):
        team: models.Team
        subscription: models.Subscription
        document_reference: models.DocumentReference


class GetSlackInstallation:
    class RequestBody(pydantic.BaseModel):
        slack_installation: SlackInstallationInput

    class ResponseBody(pydantic.BaseModel):
        team: models.Team
        slack_installation: models.SlackInstallation

class GetGithubInstallation:
    class RequestBody(pydantic.BaseModel):
        github_installation: GithubInstallationInput

    class ResponseBody(pydantic.BaseModel):
        team: models.Team
        github_installation: models.GithubInstallation

class GetAtlassianInstallation:
    class RequestBody(pydantic.BaseModel):
        atlassian_installation: AtlassianInstallationInput

    class ResponseBody(pydantic.BaseModel):
        team: models.Team
        atlassian_installation: models.AtlassianInstallation

class GetAccessToken:
    class RequestBody(pydantic.BaseModel):
        exchange_offer: AccessTokenExchangeOfferInput

    class ResponseBody(pydantic.BaseModel):
        access_token: models.AuthToken
        refresh_token: models.AuthToken

class GetAccount:
    class ResponseBody(pydantic.BaseModel):
        team: models.Team
        account: models.Account
