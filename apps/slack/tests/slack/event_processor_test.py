import http
import json
import unittest.mock

from starlette.responses import Response
from eave.stdlib.headers import EAVE_ORIGIN_HEADER, EAVE_REQUEST_ID_HEADER, EAVE_SIG_TS_HEADER, EAVE_SIGNATURE_HEADER
import eave.stdlib.requests
import eave.stdlib.signing
from eave.stdlib.eave_origins import EaveApp
from eave.stdlib.slack_api.operations import SlackEventProcessorTaskOperation
from .base import BaseTestCase


class EventsEndpointTest(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    async def test_missing_headers(self) -> None:
        slack_handler_mock = self._mock_slack_handler()

        response = await self.httpclient.request(
            SlackEventProcessorTaskOperation.config.method,
            SlackEventProcessorTaskOperation.config.path,
            json=self.anydict(),
        )

        assert response.status_code == http.HTTPStatus.BAD_REQUEST
        assert slack_handler_mock.call_count == 0

    async def test_invalid_headers(self) -> None:
        slack_handler_mock = self._mock_slack_handler()

        response = await self.httpclient.request(
            SlackEventProcessorTaskOperation.config.method,
            SlackEventProcessorTaskOperation.config.path,
            headers={
                EAVE_ORIGIN_HEADER: self.anystr(),
                EAVE_REQUEST_ID_HEADER: self.anystr(),
                EAVE_SIGNATURE_HEADER: self.anystr(),
            },
            json=self.anydict(),
        )

        assert response.status_code == http.HTTPStatus.BAD_REQUEST
        assert slack_handler_mock.call_count == 0

    async def test_valid_signature(self) -> None:
        slack_handler_mock = self._mock_slack_handler()

        request_body = self.anydict()
        eave_request_id = self.anyuuid("eave request id")
        origin = EaveApp.eave_slack_app
        eave_sig_ts = eave.stdlib.signing.make_sig_ts()
        signature_message = eave.stdlib.signing.build_message_to_sign(
            SlackEventProcessorTaskOperation.config.method,
            path=SlackEventProcessorTaskOperation.config.path,
            origin=origin,
            audience=EaveApp.eave_slack_app,
            ts=eave_sig_ts,
            request_id=eave_request_id,
            payload=json.dumps(request_body),
            team_id=None,
            account_id=None,
        )

        signature = eave.stdlib.signing.sign_b64(
            signing_key=eave.stdlib.signing.get_key(signer=origin),
            data=signature_message,
        )

        response = await self.httpclient.request(
            SlackEventProcessorTaskOperation.config.method,
            SlackEventProcessorTaskOperation.config.path,
            headers={
                EAVE_ORIGIN_HEADER: origin,
                EAVE_REQUEST_ID_HEADER: str(eave_request_id),
                EAVE_SIGNATURE_HEADER: signature,
                EAVE_SIG_TS_HEADER: str(eave_sig_ts),
            },
            json=request_body,
        )

        assert response.status_code == http.HTTPStatus.OK
        assert slack_handler_mock.call_count == 1

    async def test_invalid_signature(self) -> None:
        slack_handler_mock = self._mock_slack_handler()

        response = await self.httpclient.request(
            SlackEventProcessorTaskOperation.config.method,
            SlackEventProcessorTaskOperation.config.path,
            headers={
                EAVE_ORIGIN_HEADER: EaveApp.eave_slack_app,
                EAVE_REQUEST_ID_HEADER: self.anystr(),
                EAVE_SIGNATURE_HEADER: self.anystr("invalid signature"),
            },
            json=self.anydict(),
        )

        assert response.status_code == http.HTTPStatus.BAD_REQUEST
        assert slack_handler_mock.call_count == 0

    def _mock_slack_handler(self) -> unittest.mock.Mock:
        return self.patch(
            name="AsyncSlackRequestHandler.handle",
            patch=unittest.mock.patch(
                "eave.slack.requests.event_processor.AsyncSlackRequestHandler.handle", return_value=Response()
            ),
        )
