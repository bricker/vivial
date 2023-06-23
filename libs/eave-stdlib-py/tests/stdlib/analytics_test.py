import json
import time
from typing import Any
from typing_extensions import override
import unittest.mock
from eave.pubsub_schemas.generated.eave_event_pb2 import EaveEvent
from eave.stdlib import analytics
from eave.stdlib.config import EaveEnvironment
import eave.stdlib.logging as _l
from eave.stdlib.test_util import UtilityBaseTestCase

mut = analytics.__name__


class AnalyticsTest(UtilityBaseTestCase):
    @override
    def mock_analytics(self) -> None:
        # The base class mocks out analytics because we want it mocked out for every other test, except these ones.
        pass

    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.patch(name="publisher", patch=unittest.mock.patch(f"{mut}.PublisherClient.publish"))

        self._expected_topic_path = "projects/eavefyi-dev/topics/eave_event_topic"

    async def test_basic_publish_with_all_parameters(self):
        self.patch_env({"EAVE_ANALYTICS_ENABLED": "1"})
        fakenow = float(self.anyint("fakenow"))

        analytics.log_event(
            event_name=self.anystring("event_name"),
            event_description=self.anystring("event_description"),
            event_source=self.anystring("event_source"),
            opaque_params=self.anydict("opaque_params"),
            eave_account_id=self.anystring("eave_account_id"),
            eave_visitor_id=self.anystring("eave_visitor_id"),
            eave_team_id=self.anystring("eave_team_id"),
            event_ts=fakenow,
            ctx=_l.LogContext(),
        )

        expected_event = EaveEvent(
            event_name=self.getstr("event_name"),
            event_description=self.getstr("event_description"),
            event_source=self.getstr("event_source"),
            eave_account_id=self.getstr("eave_account_id"),
            eave_visitor_id=self.getstr("eave_visitor_id"),
            eave_team_id=self.getstr("eave_team_id"),
            opaque_params=json.dumps(self.getdict("opaque_params")),
            event_ts=fakenow,
            eave_env=EaveEnvironment.development,
        )

        mock = self.get_mock("publisher")
        assert mock.call_count == 1
        mock.assert_called_with(self._expected_topic_path, expected_event.SerializeToString())

    async def test_basic_publish_with_uuid_parameters(self):
        self.patch_env({"EAVE_ANALYTICS_ENABLED": "1"})
        self.patch(name="now", patch=unittest.mock.patch("time.time", return_value=time.time()))

        analytics.log_event(
            event_name=self.anystring("event_name"),
            event_description=self.anystring("event_description"),
            event_source=self.anystring("event_source"),
            opaque_params=self.anydict("opaque_params"),
            eave_account_id=self.anyuuid("eave_account_id"),
            eave_visitor_id=self.anyuuid("eave_visitor_id"),
            eave_team_id=self.anyuuid("eave_team_id"),
        )

        expected_event = EaveEvent(
            event_name=self.getstr("event_name"),
            event_description=self.getstr("event_description"),
            event_source=self.getstr("event_source"),
            eave_account_id=str(self.getuuid("eave_account_id")),
            eave_visitor_id=str(self.getuuid("eave_visitor_id")),
            eave_team_id=str(self.getuuid("eave_team_id")),
            opaque_params=json.dumps(self.getdict("opaque_params")),
            event_ts=self.get_mock("now").return_value,
            eave_env=EaveEnvironment.development,
        )

        mock = self.get_mock("publisher")
        assert mock.call_count == 1
        mock.assert_called_with(self._expected_topic_path, expected_event.SerializeToString())

    async def test_publish_with_minimal_params(self):
        self.patch_env({"EAVE_ANALYTICS_ENABLED": "1"})
        self.patch(name="now", patch=unittest.mock.patch("time.time", return_value=time.time()))

        eave_ctx = _l.LogContext()
        analytics.log_event(
            event_name=self.anystring("event_name"),
            event_description=self.anystring("event_description"),
            event_source=self.anystring("event_source"),
            ctx=eave_ctx,
        )

        expected_event = EaveEvent(
            event_name=self.getstr("event_name"),
            event_description=self.getstr("event_description"),
            event_source=self.getstr("event_source"),
            eave_account_id=None,
            eave_visitor_id=None,
            eave_team_id=None,
            opaque_params=json.dumps({
                "eave_ctx": eave_ctx,
            }),
            event_ts=self.get_mock("now").return_value,
            eave_env=EaveEnvironment.development,
        )

        mock = self.get_mock("publisher")
        assert mock.call_count == 1
        mock.assert_called_with(self._expected_topic_path, expected_event.SerializeToString())

    async def test_No_Context_Given(self) -> None:
        self.patch_env({"EAVE_ANALYTICS_ENABLED": "1"})
        self.patch(name="now", patch=unittest.mock.patch("time.time", return_value=time.time()))

        self.patch(patch=unittest.mock.patch("uuid.uuid4", return_value=self.anyuuid("uuid")))
        mock_ctx = _l.LogContext()

        analytics.log_event(
            event_name=self.anystring("event_name"),
            event_description=self.anystring("event_description"),
            event_source=self.anystring("event_source"),
        )

        expected_event = EaveEvent(
            event_name=self.getstr("event_name"),
            event_description=self.getstr("event_description"),
            event_source=self.getstr("event_source"),
            eave_account_id=None,
            eave_visitor_id=None,
            eave_team_id=None,
            opaque_params=json.dumps({
                "eave_ctx": mock_ctx,
            }),
            event_ts=self.get_mock("now").return_value,
            eave_env=EaveEnvironment.development,
        )

        mock = self.get_mock("publisher")
        assert mock.call_count == 1
        mock.assert_called_with(self._expected_topic_path, expected_event.SerializeToString())

    async def test_publish_with_malformed_opaque_params(self) -> None:
        self.patch_env({"EAVE_ANALYTICS_ENABLED": "1"})
        self.patch(name="now", patch=unittest.mock.patch("time.time", return_value=time.time()))

        class unserializable:
            pass

        bad_params: Any = {self.anystring("paramkey"): unserializable()}
        analytics.log_event(
            event_name=self.anystring("event_name"),
            event_description=self.anystring("event_description"),
            event_source=self.anystring("event_source"),
            opaque_params=bad_params,
        )

        expected_event = EaveEvent(
            event_name=self.getstr("event_name"),
            event_description=self.getstr("event_description"),
            event_source=self.getstr("event_source"),
            eave_account_id=None,
            eave_visitor_id=None,
            eave_team_id=None,
            opaque_params=str(bad_params),
            event_ts=self.get_mock("now").return_value,
            eave_env=EaveEnvironment.development,
        )

        mock = self.get_mock("publisher")
        assert mock.call_count == 1
        mock.assert_called_with(self._expected_topic_path, expected_event.SerializeToString())

    async def test_publish_in_dev(self):
        # "EAVE_ANALYTICS_ENABLED" is not set (None) by default
        self.patch(name="now", patch=unittest.mock.patch("time.time", return_value=time.time()))

        analytics.log_event(
            event_name=self.anystring("event_name"),
            event_description=self.anystring("event_description"),
            event_source=self.anystring("event_source"),
        )

        mock = self.get_mock("publisher")
        assert mock.call_count == 0
