from datetime import datetime
import json
from typing import Any
import unittest.mock

from google.pubsub_v1 import PubsubMessage
from eave.pubsub_schemas.generated.eave_event_pb2 import EaveEvent
from eave.stdlib import analytics
from eave.stdlib.config import EaveEnvironment
from eave.stdlib.core_api.models.account import AnalyticsAccount, AuthProvider
from eave.stdlib.core_api.models.team import AnalyticsTeam, DocumentPlatform
import eave.stdlib.logging as _l
from eave.stdlib.test_util import UtilityBaseTestCase

mut = analytics.__name__


class unserializable:
    pass


class AnalyticsTestBase(UtilityBaseTestCase):
    def mock_analytics(self) -> None:
        # The base class mocks out analytics because we want it mocked out for every other test, except these ones.
        pass

    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.mocks_publisher = self.patch(
            name="publisher", patch=unittest.mock.patch(f"{mut}.PublisherAsyncClient.publish")
        )

        self.data_now = datetime.utcnow()
        self.mocks_now = self.patch(name="now", patch=unittest.mock.patch(f"{mut}.datetime", autospec=True))
        self.mocks_now.utcnow.return_value = self.data_now

        self.mocks_analytics_enabled = self.patch_env({"EAVE_ANALYTICS_DISABLED": "0"})

        self.data_expected_topic_path = "projects/eavefyi-dev/topics/eave_event"
        self.data_team = AnalyticsTeam(
            id=self.anyuuid(),
            document_platform=DocumentPlatform.confluence,
            name=self.anystr(),
        )

        self.data_account = AnalyticsAccount(
            id=self.anyuuid(),
            auth_provider=AuthProvider.google,
            visitor_id=self.anyuuid(),
            team_id=self.data_team.id,
            opaque_utm_params=self.anydict(),
        )

        self.data_ctx = _l.LogContext()
        self.data_ctx.feature_name = self.anystr("feature_name")
        self.data_bad_params: Any = {self.anystr("paramkey"): unserializable()}


class AnalyticsTest(AnalyticsTestBase):
    def run_common_assertions(self):
        assert self.mocks_publisher.call_count == 1
        self.mocks_publisher.assert_called_with(
            topic=self.data_expected_topic_path,
            messages=[PubsubMessage(data=self.data_expected_event.SerializeToString())],
        )

    async def test_basic_publish_with_all_parameters(self):
        await analytics.log_event(
            event_name=self.anystr("event_name"),
            event_description=self.anystr("event_description"),
            event_source=self.anystr("event_source"),
            opaque_params=self.anydict("opaque_params"),
            eave_account=self.data_account,
            eave_team=self.data_team,
            ctx=self.data_ctx,
        )

        self.data_expected_event = EaveEvent(
            event_name=self.getstr("event_name"),
            event_description=self.getstr("event_description"),
            event_source=self.getstr("event_source"),
            feature_name=self.getstr("feature_name"),
            eave_account_id=str(self.data_account.id),
            eave_visitor_id=str(self.data_account.visitor_id),
            eave_team_id=str(self.data_team.id),
            eave_account=self.data_account.json(),
            eave_team=self.data_team.json(),
            opaque_params=json.dumps(self.getdict("opaque_params")),
            event_time=self.data_now.isoformat(),
            eave_env=EaveEnvironment.test,
            opaque_eave_ctx=json.dumps(self.data_ctx),
            eave_request_id=str(self.data_ctx["eave_request_id"]),
        )

        self.run_common_assertions()

    async def test_basic_publish_with_uuid_parameters(self):
        await analytics.log_event(
            event_name=self.anystr("event_name"),
            event_description=self.anystr("event_description"),
            event_source=self.anystr("event_source"),
            opaque_params=self.anydict("opaque_params"),
            eave_account=self.data_account,
            eave_team=self.data_team,
            ctx=self.data_ctx,
        )

        self.data_expected_event = EaveEvent(
            event_name=self.getstr("event_name"),
            event_description=self.getstr("event_description"),
            event_source=self.getstr("event_source"),
            feature_name=self.getstr("feature_name"),
            eave_account_id=str(self.data_account.id),
            eave_visitor_id=str(self.data_account.visitor_id),
            eave_team_id=str(self.data_team.id),
            eave_account=self.data_account.json(),
            eave_team=self.data_team.json(),
            opaque_params=json.dumps(self.getdict("opaque_params")),
            event_time=self.data_now.isoformat(),
            eave_env=EaveEnvironment.test,
            opaque_eave_ctx=json.dumps(self.data_ctx),
            eave_request_id=str(self.data_ctx["eave_request_id"]),
        )

        self.run_common_assertions()

    async def test_publish_with_minimal_params(self):
        await analytics.log_event(
            event_name=self.anystr("event_name"),
            event_description=self.anystr("event_description"),
            event_source=self.anystr("event_source"),
            ctx=self.data_ctx,
        )

        self.data_expected_event = EaveEvent(
            event_name=self.getstr("event_name"),
            event_description=self.getstr("event_description"),
            event_source=self.getstr("event_source"),
            feature_name=self.getstr("feature_name"),
            eave_account_id=None,
            eave_visitor_id=None,
            eave_team_id=None,
            eave_account=None,
            eave_team=None,
            opaque_params=None,
            event_time=self.data_now.isoformat(),
            eave_env=EaveEnvironment.test,
            opaque_eave_ctx=json.dumps(self.data_ctx),
            eave_request_id=str(self.data_ctx["eave_request_id"]),
        )

        self.run_common_assertions()

    async def test_no_context_given(self) -> None:
        # These need to be defined before uuid is patched
        event_name = self.anystr("event_name")
        event_description = self.anystr("event_description")
        event_source = self.anystr("event_source")

        self.patch(patch=unittest.mock.patch("uuid.uuid4", return_value=self.anyuuid("uuid")))

        await analytics.log_event(
            event_name=event_name,
            event_description=event_description,
            event_source=event_source,
            ctx=None,
        )

        self.data_expected_event = EaveEvent(
            event_name=self.getstr("event_name"),
            event_description=self.getstr("event_description"),
            event_source=self.getstr("event_source"),
            feature_name=None,
            eave_account_id=None,
            eave_visitor_id=None,
            eave_team_id=None,
            eave_account=None,
            eave_team=None,
            opaque_params=None,
            event_time=self.data_now.isoformat(),
            eave_env=EaveEnvironment.test,
            opaque_eave_ctx=None,
            eave_request_id=None,
        )

        self.run_common_assertions()

    async def test_publish_with_malformed_opaque_params(self) -> None:
        await analytics.log_event(
            event_name=self.anystr("event_name"),
            event_description=self.anystr("event_description"),
            event_source=self.anystr("event_source"),
            opaque_params=self.data_bad_params,
            ctx=self.data_ctx,
        )

        self.data_expected_event = EaveEvent(
            event_name=self.getstr("event_name"),
            event_description=self.getstr("event_description"),
            event_source=self.getstr("event_source"),
            feature_name=self.getstr("feature_name"),
            eave_account_id=None,
            eave_visitor_id=None,
            eave_team_id=None,
            eave_account=None,
            eave_team=None,
            opaque_params=str(self.data_bad_params),
            event_time=self.data_now.isoformat(),
            eave_env=EaveEnvironment.test,
            opaque_eave_ctx=json.dumps(self.data_ctx),
            eave_request_id=str(self.data_ctx["eave_request_id"]),
        )

        self.run_common_assertions()

    async def test_publish_in_dev(self):
        self.get_patch("env").stop()

        await analytics.log_event(
            event_name=self.anystr("event_name"),
            event_description=self.anystr("event_description"),
            event_source=self.anystr("event_source"),
            ctx=None,
        )

        assert self.mocks_publisher.call_count == 0
