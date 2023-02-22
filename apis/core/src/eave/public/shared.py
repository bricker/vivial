import enum
from typing import Optional

from pydantic import BaseModel


class DocumentPlatform(str, enum.Enum):
    eave = "eave"
    confluence = "confluence"
    google_drive = "google_drive"
    unspecified = "unspecified"

class DocumentContentInput(BaseModel):
    title: str
    content: str
    parent: Optional["DocumentContentInput"]


class SubscriptionSourcePlatform(str, enum.Enum):
    slack = "slack"


class SubscriptionSourceEvent(str, enum.Enum):
    slack_message = "slack.message"


class SubscriptionSource(BaseModel):
    platform: SubscriptionSourcePlatform
    event: SubscriptionSourceEvent
    id: str


class SubscriptionInput(BaseModel):
    source: SubscriptionSource
    context: Optional[str]


class PromptInput(BaseModel):
    prompt: str
    response: str
