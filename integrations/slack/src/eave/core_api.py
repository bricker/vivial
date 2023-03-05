import enum
from collections import namedtuple
from dataclasses import dataclass
from functools import cache
from http import HTTPStatus
from typing import Optional
from uuid import UUID

import aiohttp

import eave.util
from eave.settings import APP_SETTINGS


class DocumentPlatform(enum.Enum):
    eave = "eave"
    confluence = "confluence"


@dataclass
class DocumentReference:
    id: UUID
    document_id: str
    document_url: str

    @classmethod
    def from_json(cls, json: eave.util.JsonObject) -> "DocumentReference":
        return cls(
            id=json["id"],
            document_id=json["document_id"],
            document_url=json["document_url"],
        )


@dataclass
class Document:
    title: str
    content: str
    parent: Optional["Document"] = None

    def to_json(self) -> eave.util.JsonObject:
        return {
            "title": self.title,
            "content": self.content,
            "parent": self.parent.to_json() if self.parent is not None else None,
        }


class SubscriptionSourceEvent(enum.Enum):
    slack_message = "slack.message"


@dataclass
class SubscriptionSource:
    platform = "slack"
    event: SubscriptionSourceEvent
    id: str

    @dataclass
    class Details:
        team: str
        channel: str
        ts: str

    @property
    def details(self) -> Details:
        team, channel, ts = self.id.split("#")
        return SubscriptionSource.Details(team=team, channel=channel, ts=ts)

    @classmethod
    def from_json(cls, json: eave.util.JsonObject) -> "SubscriptionSource":
        return cls(
            id=json["id"],
            event=SubscriptionSourceEvent(json["event"]),
        )

    def to_json(self) -> eave.util.JsonObject:
        return {
            "platform": self.platform,
            "event": self.event.value,
            "id": self.id,
        }


@dataclass
class Subscription:
    id: UUID
    document_reference_id: Optional[UUID]
    source: SubscriptionSource

    @classmethod
    def from_json(cls, json: eave.util.JsonObject) -> "Subscription":
        return cls(
            id=json["id"],
            document_reference_id=json.get("document_reference_id"),
            source=SubscriptionSource.from_json(json["source"]),
        )

    def to_json(self) -> eave.util.JsonObject:
        return {
            "id": self.id,
            "document_reference_id": self.document_reference_id,
            "source": self.source.to_json(),
        }


@dataclass
class Team:
    id: UUID
    name: str
    document_platform: DocumentPlatform

    @classmethod
    def from_json(cls, json: eave.util.JsonObject) -> "Team":
        return cls(
            id=json["id"],
            name=json["name"],
            document_platform=DocumentPlatform(json["document_platform"]),
        )


class EaveCoreClient:
    api_base_url: str

    def __init__(self, api_base_url: str = APP_SETTINGS.eave_core_api_url) -> None:
        self.api_base_url = api_base_url

    class UpsertDocumentResponse:
        team: Team
        subscription: Subscription
        document_reference: DocumentReference

        def __init__(self, json: eave.util.JsonObject) -> None:
            self.team = Team.from_json(json["team"])
            self.subscription = Subscription.from_json(json["subscription"])
            self.document_reference = DocumentReference.from_json(json["document_reference"])

    async def upsert_document(self, document: Document, source: SubscriptionSource, addl_headers: dict[str,str] = {}) -> UpsertDocumentResponse:
        data = {
            "document": document.to_json(),
            "subscription": {"source": source.to_json()},
        }

        async with aiohttp.ClientSession() as session:
            resp = await session.request(
                "POST",
                f"{self.api_base_url}/documents/upsert",
                headers={
                    "eave-team-id": APP_SETTINGS.eave_team_id,
                    **addl_headers,
                },
                json=data,
            )

        json = await resp.json()
        return EaveCoreClient.UpsertDocumentResponse(json)

    class SubscriptionResponse:
        team: Team
        subscription: Subscription
        document_reference: Optional[DocumentReference] = None
        status: int
        created: bool

        def __init__(self, json: eave.util.JsonObject, status: int) -> None:
            self.team = Team.from_json(json["team"])
            self.subscription = Subscription.from_json(json["subscription"])
            self.created = status == HTTPStatus.CREATED

            drjson = json.get("document_reference")
            if drjson is not None:
                self.document_reference = DocumentReference.from_json(json["document_reference"])

    async def get_or_create_subscription(self, source: SubscriptionSource) -> SubscriptionResponse:
        async with aiohttp.ClientSession() as session:
            resp = await session.request(
                "POST",
                f"{APP_SETTINGS.eave_core_api_url}/subscriptions/create",
                headers={"eave-team-id": APP_SETTINGS.eave_team_id},
                json={
                    "subscription": {
                        "source": source.to_json(),
                    },
                },
            )

        json = await resp.json()
        return EaveCoreClient.SubscriptionResponse(json, status=resp.status)

    async def get_subscription(self, source: SubscriptionSource) -> Optional[SubscriptionResponse]:
        async with aiohttp.ClientSession() as session:
            resp = await session.request(
                "POST",
                f"{APP_SETTINGS.eave_core_api_url}/subscriptions/query",
                headers={"eave-team-id": APP_SETTINGS.eave_team_id},
                json={
                    "subscription": {
                        "source": source.to_json(),
                    },
                },
            )

        if resp.status >= 300:
            return None

        json = await resp.json()
        return EaveCoreClient.SubscriptionResponse(json, status=resp.status)


client = EaveCoreClient()
