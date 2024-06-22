"""
Class representations of the API payloads from the collectors.
We don't use automatic dataclass initializers because we want to ignore any unexpected attributes, which dataclasses don't natively allow.

Additionally, these are true representations; in other words, these class don't do any conversion to BigQuery-ready datastructures.
That happens in the RecordField classes.
"""

from dataclasses import dataclass
import json
from enum import StrEnum
from typing import Any, Self
from cryptography import fernet

from eave.collectors.core.correlation_context.base import EAVE_COLLECTOR_COOKIE_PREFIX, EAVE_ENCRYPTED_ACCOUNT_COOKIE_NAME
from eave.collectors.core.datastructures import DatabaseOperation, HttpRequestMethod
from eave.stdlib.logging import LOGGER
from eave.stdlib.typing import JsonScalar


class BrowserAction(StrEnum):
    CLICK = "CLICK"
    FORM_SUBMISSION = "FORM_SUBMISSION"
    PAGE_VIEW = "PAGE_VIEW"

    @classmethod
    def from_str(cls, s: str) -> Self | None:
        try:
            return cls.__call__(value=s.upper())
        except ValueError:
            return None

@dataclass(kw_only=True)
class DeviceBrandProperties:
    brand: str | None
    version: str | None

    @classmethod
    def from_api_payload(cls, data: dict[str, str]) -> Self:
        return cls(
            brand=data.get("brand"),
            version=data.get("version"),
        )

@dataclass(kw_only=True)
class DeviceProperties:
    user_agent: str | None
    brands: list[DeviceBrandProperties] | None
    platform: str | None
    mobile: bool | None
    form_factor: str | None
    model: str | None
    platform_version: str | None
    screen_width: int | None
    screen_height: int | None
    screen_avail_width: int | None
    screen_avail_height: int | None

    @classmethod
    def from_api_payload(cls, data: dict[str, Any]) -> Self:
        return cls(
            user_agent=data.get("user_agent"),
            platform=data.get("platform"),
            mobile=data.get("mobile"),
            form_factor=data.get("form_factor"),
            model=data.get("model"),
            platform_version=data.get("platform_version"),
            screen_width=data.get("screen_width"),
            screen_height=data.get("screen_height"),
            screen_avail_width=data.get("screen_avail_width"),
            screen_avail_height=data.get("screen_avail_height"),
            brands=(
                [DeviceBrandProperties.from_api_payload(d) for d in v]
                if (v := data.get("brands")) and isinstance(v, list)
                else None
            ),
        )

@dataclass(kw_only=True)
class CurrentPageProperties:
    url: str | None
    title: str | None
    pageview_id: str | None

    @classmethod
    def from_api_payload(cls, data: dict[str, Any]) -> Self:
        return cls(
            title=data.get("title"),
            pageview_id=data.get("pageview_id"),
            url=data.get("url"),
        )

@dataclass(kw_only=True)
class SessionProperties:
    id: str | None
    start_timestamp: float | None

    @classmethod
    def from_api_payload(cls, data: dict[str, Any]) -> Self:
        return cls(
            id=data.get("id"),
            start_timestamp=data.get("start_timestamp"),
        )

@dataclass(kw_only=True)
class TrafficSourceProperties:
    timestamp: float | None
    browser_referrer: str | None
    tracking_params: dict[str, str | None] | None

    @classmethod
    def from_api_payload(cls, data: dict[str, Any]) -> Self:
        return cls(
            timestamp=data.get("timestamp"),
            browser_referrer=data.get("browser_referrer"),
            tracking_params=data.get("tracking_params"),
        )

@dataclass(kw_only=True)
class TargetProperties:
    type: str | None
    id: str | None
    content: str | None
    attributes: dict[str, str | None] | None

    @classmethod
    def from_api_payload(cls, data: dict[str, Any]) -> Self:
        return cls(
            type=data.get("type"),
            id=data.get("id"),
            content=data.get("content"),
            attributes=data.get("attributes"),
        )

@dataclass(kw_only=True)
class AccountProperties:
    account_id: str | None
    extra: dict[str, str] | None

    @classmethod
    def from_api_payload(cls, data: dict[str, str]) -> Self:
        data_copy = data.copy()
        return cls(
            account_id=data_copy.pop("account_id", None),
            extra=data_copy,
        )

@dataclass(kw_only=True)
class CorrelationContext:
    session: SessionProperties | None
    traffic_source: TrafficSourceProperties | None
    visitor_id: str | None
    account: AccountProperties | None
    extra: dict[str, Any] | None

    @classmethod
    def from_api_payload(cls, data: dict[str, str], symmetric_encryption_key: bytes) -> Self:
        session = None
        traffic_source = None
        account = None
        visitor_id = None

        data_copy = data.copy()

        if (v := data_copy.pop(f"{EAVE_COLLECTOR_COOKIE_PREFIX}session"), None) and isinstance(v, str):
            try:
                us = json.loads(v)
                if isinstance(us, dict):
                    session = SessionProperties.from_api_payload(us)
            except Exception as e:
                # Probably JSON parse error
                LOGGER.exception(e)

        if (v := data_copy.pop(f"{EAVE_COLLECTOR_COOKIE_PREFIX}traffic_source"), None) and isinstance(v, str):
            try:
                us = json.loads(v)
                if isinstance(us, dict):
                    traffic_source = TrafficSourceProperties.from_api_payload(us)
            except Exception as e:
                # Probably JSON parse error
                LOGGER.exception(e)

        if (v := data_copy.pop(f"{EAVE_COLLECTOR_COOKIE_PREFIX}visitor_id"), None) and isinstance(v, str):
            visitor_id = v

        if (v := data_copy.pop(EAVE_ENCRYPTED_ACCOUNT_COOKIE_NAME), None) and isinstance(v, str):
            try:
                # TTL should NOT be considered here, because the encrypted value may come from long-lived cookies.
                # Regardless, this encryption is purely for obfuscation in the browser, not for message integrity, so TTL doesn't really matter anyways.
                decrypted_val = fernet.Fernet(symmetric_encryption_key).decrypt(v, ttl=None).decode()
                us = json.loads(decrypted_val)
                if isinstance(us, dict):
                    account = AccountProperties.from_api_payload(us)
            except Exception as e:
                # Either JSON parse error or decryption error.
                # The account attribute will be empty.
                LOGGER.exception(e)

        # Stuff anything else into self.extra, with the eave cookie prefix removed.
        extra = {k.removeprefix(EAVE_COLLECTOR_COOKIE_PREFIX): v for k, v in data_copy.items()}

        return cls(
            session=session,
            traffic_source=traffic_source,
            visitor_id=visitor_id,
            account=account,
            extra=extra,
        )

@dataclass(kw_only=True)
class BrowserEventPayload:
    action: BrowserAction | None
    timestamp: float | None
    target: TargetProperties | None
    device: DeviceProperties | None
    current_page: CurrentPageProperties | None
    extra: dict[str, JsonScalar | None] | None
    corr_ctx: CorrelationContext | None

    @classmethod
    def from_api_payload(cls, data: dict[str, Any]) -> Self:
        return cls(
            timestamp=data.get("timestamp"),
            extra=data.get("extra"),
            action=(
                BrowserAction.from_str(v)
                if (v := data.get("action"))
                else None
            ),
            target=(
                TargetProperties.from_api_payload(v)
                if (v := data.get("target")) and isinstance(v, dict)
                else None
            ),
            device=(
                DeviceProperties.from_api_payload(v)
                if (v := data.get("device")) and isinstance(v, dict)
                else None
            ),
            current_page=(
                CurrentPageProperties.from_api_payload(v)
                if (v := data.get("current_page")) and isinstance(v, dict)
                else None
            ),
            corr_ctx=(
                CorrelationContext.from_api_payload(v)
                if (v := data.get("corr_ctx")) and isinstance(v, dict)
                else None
            ),
        )


@dataclass(kw_only=True)
class DatabaseEventPayload:
    timestamp: float | None
    operation: DatabaseOperation | None
    db_name: str | None
    table_name: str | None
    statement: str | None
    statement_values: dict[str, Any] | None
    corr_ctx: CorrelationContext | None

    @classmethod
    def from_api_payload(cls, data: dict[str, Any]) -> Self:
        return cls(
            timestamp=data.get("timestamp"),
            db_name=data.get("db_name"),
            table_name=data.get("table_name"),
            statement=data.get("statement"),
            statement_values=data.get("statement_values"),
            operation = DatabaseOperation.from_str(v) if (v := data.get("operation")) else None,
            corr_ctx=(
                CorrelationContext.from_api_payload(v)
                if (v := data.get("corr_ctx")) and isinstance(v, dict)
                else None
            ),
        )

@dataclass(kw_only=True)
class HttpServerEventPayload:
    timestamp: float | None
    corr_ctx: CorrelationContext | None
    request_method: HttpRequestMethod | None
    request_url: str | None
    request_headers: dict[str, str | None] | None
    request_payload: str | None

    @classmethod
    def from_api_payload(cls, data: dict[str, Any]) -> Self:
        return cls(
            timestamp=data.get("timestamp"),
            request_url=data.get("request_url"),
            request_headers=data.get("request_headers"),
            request_payload=data.get("request_payload"),
            request_method = HttpRequestMethod.from_str(v) if (v := data.get("request_method")) else None,
            corr_ctx=(
                CorrelationContext.from_api_payload(v)
                if (v := data.get("corr_ctx")) and isinstance(v, dict)
                else None
            ),
        )
