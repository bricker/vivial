import dataclasses
import logging
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, ClassVar, Literal, Self

from eave.collectors.core.logging import EAVE_LOGGER

from .json import JsonObject, compact_json

class DatabaseOperation(StrEnum):
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    SELECT = "SELECT"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_str(cls, s: str) -> Self | None:
        try:
            return cls.__call__(value=s.upper())
        except ValueError as e:
            EAVE_LOGGER.warning(e)
            return None

class BrowserAction(StrEnum):
    CLICK = "CLICK"
    FORM_SUBMIT = "FORM_SUBMIT"
    NAVIGATION = "NAVIGATION"

    @classmethod
    def from_str(cls, s: str) -> Self | None:
        try:
            return cls.__call__(value=s.upper())
        except ValueError as e:
            EAVE_LOGGER.warning(e)
            return None

class EventType(StrEnum):
    db_event = "db_event"
    http_server_event = "http_server_event"
    http_client_event = "http_client_event"
    browser_event = "browser_event"

@dataclass
class KeyValueDict:
    key: str
    value: str | None

    @classmethod
    def list_from_dict(cls, d: dict[str, Any]) -> list[Self]:
        return [cls(k, v) for k, v in d.items()]

@dataclass(kw_only=True)
class Geolocation:
    region: str | None = None
    subdivision: str | None = None
    city: str | None = None
    coordinates: str | None = None

@dataclass(kw_only=True)
class DeviceBrandProperties:
    brand: str | None = None
    version: str | None = None

@dataclass(kw_only=True)
class DeviceProperties:
  user_agent: str | None = None
  brands: list[DeviceBrandProperties] | None = None
  platform: str | None = None
  mobile: bool | None = None
  form_factor: str | None = None
  model: str | None = None
  platform_version: str | None = None
  screen_width: int | None = None
  screen_height: int | None = None
  screen_avail_width: int | None = None
  screen_avail_height: int | None = None


@dataclass(kw_only=True)
class PageProperties:
  current_url: str | None = None
  current_title: str | None = None
  pageview_id: str | None = None
  current_query_params: list[KeyValueDict] | None = None


@dataclass(kw_only=True)
class SessionProperties:
  id: str | None = None
  start_timestamp: int | None = None
  duration_ms: int | None = None


@dataclass(kw_only=True)
class UserProperties:
  id: str | None = None
  visitor_id: str | None = None


@dataclass(kw_only=True)
class DiscoveryProperties:
  timestamp: int | None = None
  browser_referrer: str | None = None
  gclid: str | None = None
  fbclid: str | None = None
  msclkid: str | None = None
  campaign: str | None = None
  source: str | None = None
  medium: str | None = None
  term: str | None = None
  content: str | None = None
  extra_utm_params: list[KeyValueDict] | None = None


@dataclass(kw_only=True)
class TargetProperties:
  type: str | None = None
  id: str | None = None
  text: str | None = None
  attributes: list[KeyValueDict] | None = None


@dataclass(kw_only=True)
class EventPayload:
    event_type: ClassVar[EventType]

    timestamp: float | None
    session: SessionProperties | None = None
    user: UserProperties | None = None
    discovery: DiscoveryProperties | None = None

    def to_dict(self) -> JsonObject:
        return dataclasses.asdict(self)

    def to_json(self) -> str:
        return compact_json(self.to_dict())


@dataclass(kw_only=True)
class BrowserEventPayload(EventPayload):
    event_type: ClassVar[EventType] = EventType.browser_event

    action: str | None = None
    target: TargetProperties | None = None
    device: DeviceProperties | None = None
    page: PageProperties | None = None
    extra: list[KeyValueDict] | None = None
    geo: Geolocation | None = None
    client_ip: str | None = None

@dataclass(kw_only=True)
class DatabaseEventPayload(EventPayload):
    event_type: ClassVar[EventType] = EventType.db_event

    statement: str | None = None
    db_name: str | None = None
    table_name: str | None = None
    operation: str | None = None
    parameters: list[KeyValueDict] | None = None


@dataclass(kw_only=True)
class HttpServerEventPayload(EventPayload):
    """Data about a request being handled by server application code"""
    event_type: ClassVar[EventType] = EventType.http_server_event

    request_method: str | None = None
    request_url: str | None = None
    request_headers: list[KeyValueDict] | None = None
    request_payload: str | None = None


@dataclass
class HttpClientEventPayload(EventPayload):
    """Data about requests made by application code"""
    event_type: ClassVar[EventType] = EventType.http_client_event

    request_method: str | None = None
    request_url: str | None = None
    request_headers: list[KeyValueDict] | None = None
    request_payload: str | None = None


@dataclass
class DataIngestRequestBody:
    events: dict[str, list[JsonObject]]
    """map from event_type name to list of events of that type"""

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Self:
        return cls(
            events=data["events"],
        )

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    def to_json(self) -> str:
        return compact_json(self.to_dict())
