from typing import Any, Optional

import pydantic

from . import models


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

class SlackSourceInput(pydantic.BaseModel):
    slack_team_id: str

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


class UpsertDocument:
    class RequestBody(pydantic.BaseModel):
        document: DocumentInput
        subscription: SubscriptionInput

    class ResponseBody(pydantic.BaseModel):
        team: models.Team
        subscription: models.Subscription
        document_reference: models.DocumentReference

# TODO: copy to ts
class GetSlackSource:
    class RequestBody(pydantic.BaseModel):
        slack_source: SlackSourceInput

    class ResponseBody(pydantic.BaseModel):
        slack_source: models.SlackSource
