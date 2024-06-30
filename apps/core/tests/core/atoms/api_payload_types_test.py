import json

from eave.collectors.core.correlation_context.base import (
    EAVE_COLLECTOR_ACCOUNT_ID_ATTR_NAME,
    EAVE_COLLECTOR_COOKIE_PREFIX,
    EAVE_COLLECTOR_ENCRYPTED_ACCOUNT_COOKIE_PREFIX,
    CorrelationContextAttr,
)
from eave.collectors.core.datastructures import DatabaseOperation, HttpRequestMethod
from eave.core.internal.atoms.models.api_payload_types import (
    AccountProperties,
    BrowserAction,
    BrowserEventPayload,
    CorrelationContext,
    CurrentPageProperties,
    DatabaseEventPayload,
    DeviceBrandProperties,
    DeviceProperties,
    HttpServerEventPayload,
    SessionProperties,
    TargetProperties,
    TrafficSourceProperties,
)
from eave.core.internal.orm.client_credentials import ClientCredentialsOrm, ClientScope
from eave.stdlib.logging import LogContext

from ..base import BaseTestCase

class TestAtomApiTypes(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        async with self.db_session.begin() as s:
            self._team = await self.make_team(session=s)
            self._client_credentials = await ClientCredentialsOrm.create(
                session=s,
                team_id=self._team.id,
                description=self.anystr(),
                scope=ClientScope.readwrite,
            )

    async def test_device_brand_properties(self) -> None:
        e = DeviceBrandProperties.from_api_payload({})
        assert e.brand is None
        assert e.version is None

        e = DeviceBrandProperties.from_api_payload(
            {
                "brand": self.anystr("device_brand.brand"),
                "version": self.anystr("device_brand.version"),
                self.anystr("unrecognized attribute"): self.anystr(),
            }
        )
        assert e.brand == self.getstr("device_brand.brand")
        assert e.version == self.getstr("device_brand.version")

    async def test_device_properties(self) -> None:
        e = DeviceProperties.from_api_payload({})
        assert e.user_agent is None
        assert e.brands is None
        assert e.platform is None
        assert e.mobile is None
        assert e.form_factor is None
        assert e.model is None
        assert e.platform_version is None
        assert e.screen_width is None
        assert e.screen_height is None
        assert e.screen_avail_width is None
        assert e.screen_avail_height is None

        e = DeviceProperties.from_api_payload(
            {
                "user_agent": self.anystr("device.user_agent"),
                "brands": [
                    {
                        "brand": self.anystr("device.brands[0].brand"),
                        "version": self.anystr("device.brands[0].version"),
                        self.anystr("unrecognized attribute 1"): self.anystr(),
                    }
                ],
                "platform": self.anystr("device.platform"),
                "mobile": self.anybool("device.mobile"),
                "form_factor": self.anystr("device.form_factor"),
                "model": self.anystr("device.model"),
                "platform_version": self.anystr("device.platform_version"),
                "screen_width": self.anyint("device.screen_width"),
                "screen_height": self.anyint("device.screen_height"),
                "screen_avail_width": self.anyint("device.screen_avail_width"),
                "screen_avail_height": self.anyint("device.screen_avail_height"),
                self.anystr("unrecognized attribute 2"): self.anystr(),
            }
        )
        assert e.user_agent == self.getstr("device.user_agent")
        assert e.brands is not None
        assert len(e.brands) == 1
        assert e.brands[0].brand == self.getstr("device.brands[0].brand")
        assert e.brands[0].version == self.getstr("device.brands[0].version")
        assert e.platform == self.getstr("device.platform")
        assert e.mobile == self.getbool("device.mobile")
        assert e.form_factor == self.getstr("device.form_factor")
        assert e.model == self.getstr("device.model")
        assert e.platform_version == self.getstr("device.platform_version")
        assert e.screen_width == self.getint("device.screen_width")
        assert e.screen_height == self.getint("device.screen_height")
        assert e.screen_avail_width == self.getint("device.screen_avail_width")
        assert e.screen_avail_height == self.getint("device.screen_avail_height")

    async def test_current_page_properties(self):
        e = CurrentPageProperties.from_api_payload({})
        assert e.url is None
        assert e.title is None
        assert e.pageview_id is None

        e = CurrentPageProperties.from_api_payload(
            {
                "url": self.anyurl("current_page.url"),
                "title": self.anystr("current_page.title"),
                "pageview_id": self.anystr("current_page.pageview_id"),
                self.anystr("unrecognized attribute"): self.anystr(),
            }
        )
        assert e.url == self.geturl("current_page.url")
        assert e.title == self.getstr("current_page.title")
        assert e.pageview_id == self.getstr("current_page.pageview_id")

    async def test_session_properties(self):
        e = SessionProperties.from_api_payload({})
        assert e.id is None
        assert e.start_timestamp is None

        e = SessionProperties.from_api_payload(
            {
                "id": self.anystr("session.id"),
                "start_timestamp": self.anytime("session.start_timestamp"),
                self.anystr("unrecognized attribute"): self.anystr(),
            }
        )
        assert e.id == self.getstr("session.id")
        assert e.start_timestamp == self.gettime("session.start_timestamp")

    async def test_traffic_source_properties(self):
        e = TrafficSourceProperties.from_api_payload({})
        assert e.timestamp is None
        assert e.browser_referrer is None
        assert e.tracking_params is None

        e = TrafficSourceProperties.from_api_payload(
            {
                "timestamp": self.anytime("traffic_source.timestamp"),
                "browser_referrer": self.anystr("traffic_source.browser_referrer"),
                "tracking_params": self.anydict("traffic_source.tracking_params"),
                self.anystr("unrecognized attribute"): self.anystr(),
            }
        )
        assert e.timestamp == self.gettime("traffic_source.timestamp")
        assert e.browser_referrer == self.getstr("traffic_source.browser_referrer")
        assert e.tracking_params == self.getdict("traffic_source.tracking_params")

    async def test_target_properties(self):
        e = TargetProperties.from_api_payload({})
        assert e.type is None
        assert e.id is None
        assert e.content is None
        assert e.attributes is None

        e = TargetProperties.from_api_payload(
            {
                "type": self.anystr("target.type"),
                "id": self.anystr("target.id"),
                "content": self.anystr("target.content"),
                "attributes": self.anydict("target.attributes"),
                self.anystr("unrecognized attribute"): self.anystr(),
            }
        )
        assert e.type == self.getstr("target.type")
        assert e.id == self.getstr("target.id")
        assert e.content == self.getstr("target.content")
        assert e.attributes == self.getdict("target.attributes")

    async def test_account_properties(self):
        e = AccountProperties.from_api_payload({})
        assert e.account_id is None
        assert e.extra is None

        e = AccountProperties.from_api_payload(
            {
                "account_id": self.anystr("account.account_id"),
                self.anystr("account.extra.0.key"): self.anystr("account.extra.0.value"),
            }
        )
        assert e.account_id == self.getstr("account.account_id")
        assert e.extra == {
            self.getstr("account.extra.0.key"): self.getstr("account.extra.0.value"),
        }

    async def test_correlation_context(self):
        e = CorrelationContext.from_api_payload({}, decryption_key=self.anysha256())
        assert e.session is None
        assert e.traffic_source is None
        assert e.account is None
        assert e.visitor_id is None
        assert e.extra is None

        e = CorrelationContext.from_api_payload(
            {
                f"{EAVE_COLLECTOR_COOKIE_PREFIX}visitor_id": self.anystr("corr_ctx.visitor_id"),
                f"{EAVE_COLLECTOR_COOKIE_PREFIX}session": json.dumps(
                    {
                        "id": self.anystr("corr_ctx.session.id"),
                        self.anystr("unrecognized attribute 1"): self.anystr(),
                    }
                ),
                f"{EAVE_COLLECTOR_COOKIE_PREFIX}traffic_source": json.dumps(
                    {
                        "browser_referrer": self.anystr("corr_ctx.traffic_source.browser_referrer"),
                        self.anystr("unrecognized attribute 2"): self.anystr(),
                    }
                ),
                f"{EAVE_COLLECTOR_ENCRYPTED_ACCOUNT_COOKIE_PREFIX}{self.anystr("acct key 1")}": CorrelationContextAttr(
                    key=EAVE_COLLECTOR_ACCOUNT_ID_ATTR_NAME,
                    value=self.anystr("corr_ctx.account.account_id"),
                ).to_encrypted(encryption_key=self._client_credentials.decryption_key),
                f"{EAVE_COLLECTOR_ENCRYPTED_ACCOUNT_COOKIE_PREFIX}{self.anystr("acct key 2")}": CorrelationContextAttr(
                    key=self.anystr("corr_ctx.account.extra.0.key"),
                    value=self.anystr("corr_ctx.account.extra.0.value"),
                ).to_encrypted(encryption_key=self._client_credentials.decryption_key),
                self.anystr("corr_ctx.extra.0.key"): self.anystr("corr_ctx.extra.0.value"),
            },
            decryption_key=self._client_credentials.decryption_key,
        )
        assert e.visitor_id == self.getstr("corr_ctx.visitor_id")
        assert e.session is not None
        assert e.session.id == self.getstr("corr_ctx.session.id")
        assert e.traffic_source is not None
        assert e.traffic_source.browser_referrer == self.getstr("corr_ctx.traffic_source.browser_referrer")
        assert e.account is not None
        assert e.account.account_id == self.getstr("corr_ctx.account.account_id")
        assert e.account.extra == {
            self.getstr("corr_ctx.account.extra.0.key"): self.getstr("corr_ctx.account.extra.0.value"),
        }
        assert e.extra == {
            self.getstr("corr_ctx.extra.0.key"): self.getstr("corr_ctx.extra.0.value"),
        }

    async def test_correlation_context_invalid_data(self):
        # test with non-dict values
        e = CorrelationContext.from_api_payload(
            {
                f"{EAVE_COLLECTOR_COOKIE_PREFIX}session": json.dumps(self.anylist()),
                f"{EAVE_COLLECTOR_COOKIE_PREFIX}traffic_source": json.dumps(self.anylist()),
            },
            decryption_key=self.anysha256(),
        )
        assert e.session is None
        assert e.traffic_source is None

        # test with invalid JSON docs
        e = CorrelationContext.from_api_payload(
            {
                f"{EAVE_COLLECTOR_COOKIE_PREFIX}session": self.anystr(),
                f"{EAVE_COLLECTOR_COOKIE_PREFIX}traffic_source": self.anystr(),
            },
            decryption_key=self.anysha256(),
        )
        assert e.session is None
        assert e.traffic_source is None

        # test with unencrypted account values
        e = CorrelationContext.from_api_payload(
            {
                f"{EAVE_COLLECTOR_ENCRYPTED_ACCOUNT_COOKIE_PREFIX}{self.anystr()}": json.dumps(
                    {
                        EAVE_COLLECTOR_ACCOUNT_ID_ATTR_NAME: self.anystr(),
                    }
                ),
            },
            decryption_key=self._client_credentials.decryption_key,
        )
        assert e.account is None

        # test with invalid decryption key
        e = CorrelationContext.from_api_payload(
            {
                f"{EAVE_COLLECTOR_ENCRYPTED_ACCOUNT_COOKIE_PREFIX}{self.anystr()}": CorrelationContextAttr(
                    key=EAVE_COLLECTOR_ACCOUNT_ID_ATTR_NAME,
                    value=self.anystr("corr_ctx.account.account_id"),
                ).to_encrypted(encryption_key=self._client_credentials.decryption_key),
            },
            decryption_key=self.anysha256(),
        )
        assert e.account is None

    async def test_browser_event_payload(self):
        e = BrowserEventPayload.from_api_payload({}, decryption_key=self.anysha256())
        assert e.action is None
        assert e.timestamp is None
        assert e.target is None
        assert e.device is None
        assert e.current_page is None
        assert e.extra is None
        assert e.corr_ctx is None

        e = BrowserEventPayload.from_api_payload(
            {
                "action": "CLICK",
                "timestamp": self.anytime("event.timestamp"),
                "target": {
                    "id": self.anystr("event.target.id"),
                    self.anystr("unrecognized attribute 1"): self.anystr(),
                },
                "device": {
                    "user_agent": self.anystr("event.device.user_agent"),
                    self.anystr("unrecognized attribute 2"): self.anystr(),
                },
                "current_page": {
                    "url": self.anyurl("event.current_page.url"),
                    self.anystr("unrecognized attribute 3"): self.anystr(),
                },
                "extra": self.anydict("event.extra"),
                "corr_ctx": {
                    f"{EAVE_COLLECTOR_COOKIE_PREFIX}visitor_id": self.anystr("corr_ctx.visitor_id"),
                    f"{EAVE_COLLECTOR_ENCRYPTED_ACCOUNT_COOKIE_PREFIX}{self.anystr("acct key 1")}": CorrelationContextAttr(
                        key=EAVE_COLLECTOR_ACCOUNT_ID_ATTR_NAME,
                        value=self.anystr("corr_ctx.account.account_id"),
                    ).to_encrypted(encryption_key=self._client_credentials.decryption_key),
                },
                self.anystr("unrecognized attribute 5"): self.anystr(),
            },
            decryption_key=self._client_credentials.decryption_key,
        )
        assert e.action == BrowserAction.CLICK
        assert e.timestamp == self.gettime("event.timestamp")
        assert e.target is not None
        assert e.target.id == self.getstr("event.target.id")
        assert e.device is not None
        assert e.device.user_agent == self.getstr("event.device.user_agent")
        assert e.current_page is not None
        assert e.current_page.url == self.geturl("event.current_page.url")
        assert e.extra == self.getdict("event.extra")
        assert e.corr_ctx is not None
        assert e.corr_ctx.visitor_id == self.getstr("corr_ctx.visitor_id")
        assert e.corr_ctx.account is not None
        assert e.corr_ctx.account.account_id == self.getstr("corr_ctx.account.account_id")

        # invalid action
        e = BrowserEventPayload.from_api_payload(
            {
                "action": self.anystr("invalid action"),
            },
            decryption_key=self.anysha256(),
        )
        assert e.action is None

        # invalid decryption key
        e = BrowserEventPayload.from_api_payload(
            {
                "corr_ctx": {
                    f"{EAVE_COLLECTOR_ENCRYPTED_ACCOUNT_COOKIE_PREFIX}{self.anystr()}": CorrelationContextAttr(
                        key=EAVE_COLLECTOR_ACCOUNT_ID_ATTR_NAME,
                        value=self.anystr(),
                    ).to_encrypted(encryption_key=self._client_credentials.decryption_key),
                },
            },
            decryption_key=self.anysha256(),
        )

        assert e.corr_ctx is not None
        assert e.corr_ctx.account is None

    async def test_database_event_payload(self):
        e = DatabaseEventPayload.from_api_payload({}, decryption_key=self.anysha256())
        assert e.timestamp is None
        assert e.operation is None
        assert e.db_name is None
        assert e.table_name is None
        assert e.statement is None
        assert e.statement_values is None
        assert e.corr_ctx is None

        e = DatabaseEventPayload.from_api_payload(
            {
                "timestamp": self.anytime("event.timestamp"),
                "operation": DatabaseOperation.INSERT,
                "db_name": self.anystr("event.db_name"),
                "table_name": self.anystr("event.table_name"),
                "statement": self.anystr("event.statement"),
                "statement_values": {
                    self.anystr("event.statement_values.0.key"): self.anyint("event.statement_values.0.value"),
                    self.anystr("event.statement_values.1.key"): self.anystr("event.statement_values.1.value"),
                },
                "corr_ctx": {
                    f"{EAVE_COLLECTOR_COOKIE_PREFIX}visitor_id": self.anystr("corr_ctx.visitor_id"),
                    f"{EAVE_COLLECTOR_ENCRYPTED_ACCOUNT_COOKIE_PREFIX}{self.anystr("acct key 1")}": CorrelationContextAttr(
                        key=EAVE_COLLECTOR_ACCOUNT_ID_ATTR_NAME,
                        value=self.anystr("corr_ctx.account.account_id"),
                    ).to_encrypted(encryption_key=self._client_credentials.decryption_key),
                },
                self.anystr("unrecognized attribute 5"): self.anystr(),
            },
            decryption_key=self._client_credentials.decryption_key,
        )
        assert e.timestamp == self.gettime("event.timestamp")
        assert e.operation == "INSERT"
        assert e.db_name == self.getstr("event.db_name")
        assert e.table_name == self.getstr("event.table_name")
        assert e.statement == self.getstr("event.statement")
        assert e.statement_values == {
            self.getstr("event.statement_values.0.key"): self.getint("event.statement_values.0.value"),
            self.getstr("event.statement_values.1.key"): self.getstr("event.statement_values.1.value"),
        }
        assert e.corr_ctx is not None
        assert e.corr_ctx.visitor_id == self.getstr("corr_ctx.visitor_id")
        assert e.corr_ctx.account is not None
        assert e.corr_ctx.account.account_id == self.getstr("corr_ctx.account.account_id")

        # invalid operation
        e = DatabaseEventPayload.from_api_payload(
            {
                "operation": self.anystr("invalid operation"),
            },
            decryption_key=self.anysha256(),
        )
        assert e.operation is None

    async def test_http_server_event_payload(self):
        e = HttpServerEventPayload.from_api_payload({}, decryption_key=self.anysha256())
        assert e.timestamp is None
        assert e.request_method is None
        assert e.request_url is None
        assert e.request_headers is None
        assert e.request_payload is None
        assert e.corr_ctx is None

        e = HttpServerEventPayload.from_api_payload(
            {
                "timestamp": self.anytime("event.timestamp"),
                "request_method": "POST",
                "request_url": self.anyurl("event.request_url"),
                "request_headers": {
                    self.anystr("event.request_headers.0.key"): self.anystr("event.request_headers.0.value"),
                },
                "request_payload": self.anyjson("event.request_payload"),
                "corr_ctx": {
                    f"{EAVE_COLLECTOR_COOKIE_PREFIX}visitor_id": self.anystr("corr_ctx.visitor_id"),
                    f"{EAVE_COLLECTOR_ENCRYPTED_ACCOUNT_COOKIE_PREFIX}{self.anystr("acct key 1")}": CorrelationContextAttr(
                        key=EAVE_COLLECTOR_ACCOUNT_ID_ATTR_NAME,
                        value=self.anystr("corr_ctx.account.account_id"),
                    ).to_encrypted(encryption_key=self._client_credentials.decryption_key),
                },
                self.anystr("unrecognized attribute 5"): self.anystr(),
            },
            decryption_key=self._client_credentials.decryption_key,
        )
        assert e.timestamp == self.gettime("event.timestamp")
        assert e.request_method == HttpRequestMethod.POST
        assert e.request_url == self.geturl("event.request_url")
        assert e.request_headers == {
            self.getstr("event.request_headers.0.key"): self.getstr("event.request_headers.0.value"),
        }
        assert e.request_payload == self.getjson("event.request_payload")
        assert e.corr_ctx is not None
        assert e.corr_ctx.visitor_id == self.getstr("corr_ctx.visitor_id")
        assert e.corr_ctx.account is not None
        assert e.corr_ctx.account.account_id == self.getstr("corr_ctx.account.account_id")

        # invalid request method
        e = HttpServerEventPayload.from_api_payload(
            {
                "request_method": self.anystr("invalid request method"),
            },
            decryption_key=self.anysha256(),
        )
        assert e.request_method is None
