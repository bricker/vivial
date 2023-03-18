from typing import Optional
import pydantic
from . import models
from .. import util

class DocumentInput(pydantic.BaseModel):
    title: str
    content: str
    parent: Optional["DocumentInput"] = None

class DocumentReferenceInput(pydantic.BaseModel):
    id: pydantic.UUID4

class SubscriptionInput(pydantic.BaseModel):
    source: models.SubscriptionSource

class CreateAccessRequest:
    class RequestBody(pydantic.BaseModel):
        visitor_id: Optional[pydantic.UUID4]
        email: pydantic.EmailStr
        opaque_input: Optional[util.JsonObject]

class GetSubscription:
    class RequestBody(pydantic.BaseModel):
        subscription: SubscriptionInput

    class ResponseBody(pydantic.BaseModel):
        team: models.Team
        subscription: models.Subscription
        document_reference: Optional[models.DocumentReference]

class CreateSubscription:
    class RequestBody(pydantic.BaseModel):
        subscription: SubscriptionInput
        document_reference: Optional[DocumentReferenceInput]

    class ResponseBody(pydantic.BaseModel):
        team: models.Team
        subscription: models.Subscription
        document_reference: Optional[models.DocumentReference]

class UpsertDocument:
    class RequestBody(pydantic.BaseModel):
        document: DocumentInput
        subscription: SubscriptionInput

    class ResponseBody(pydantic.BaseModel):
        team: models.Team
        subscription: models.Subscription
        document_reference: models.DocumentReference
