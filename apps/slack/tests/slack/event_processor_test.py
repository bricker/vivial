import http
import json
import unittest.mock

from starlette.responses import Response
from eave.stdlib.core_api.client import build_message_to_sign
import eave.stdlib
from eave.stdlib.eave_origins import EaveOrigin
from .base import BaseTestCase


class EventsEndpointTest(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    async def test_missing_headers(self) -> None:
        slack_handler_mock = self._mock_slack_handler()

        response = await self.httpclient.request(
            "POST",
            "/_tasks/slack-events",
            json=self.anydict(),
        )

        assert response.status_code == http.HTTPStatus.OK
        assert slack_handler_mock.call_count == 0

    async def test_invalid_headers(self) -> None:
        slack_handler_mock = self._mock_slack_handler()

        response = await self.httpclient.request(
            "POST",
            "/_tasks/slack-events",
            headers={
                "eave-origin": self.anystring(),
                "eave-request-id": self.anystring(),
                "eave-signature": self.anystring(),
            },
            json=self.anydict(),
        )

        assert response.status_code == http.HTTPStatus.OK
        assert slack_handler_mock.call_count == 0

    async def test_valid_signature(self) -> None:
        slack_handler_mock = self._mock_slack_handler()

        request_body = self.anydict()
        eave_request_id = self.anystring("eave request id")
        origin = EaveOrigin.eave_slack_app
        signature_message = build_message_to_sign(
            method="POST",
            origin=origin,
            request_id=eave_request_id,
            url="/_tasks/slack-events",
            payload=json.dumps(request_body),
            team_id=None,
            account_id=None,
        )

        signature = eave.stdlib.signing.sign_b64(
            signing_key=eave.stdlib.signing.get_key(signer=origin),
            data=signature_message,
        )

        response = await self.httpclient.request(
            "POST",
            "/_tasks/slack-events",
            headers={
                "eave-origin": origin,
                "eave-request-id": eave_request_id,
                "eave-signature": signature,
            },
            json=request_body,
        )

        assert response.status_code == http.HTTPStatus.OK
        assert slack_handler_mock.call_count == 1

    async def test_invalid_signature(self) -> None:
        slack_handler_mock = self._mock_slack_handler()

        response = await self.httpclient.request(
            "POST",
            "/_tasks/slack-events",
            headers={
                "eave-origin": EaveOrigin.eave_slack_app,
                "eave-request-id": self.anystring(),
                "eave-signature": self.anystring("invalid signature"),
            },
            json=self.anydict(),
        )

        assert response.status_code == http.HTTPStatus.OK
        assert slack_handler_mock.call_count == 0

    def _mock_slack_handler(self) -> unittest.mock.Mock:
        return self.patch(
            name="AsyncSlackRequestHandler.handle",
            patch=unittest.mock.patch(
                "eave.slack.requests.event_processor.AsyncSlackRequestHandler.handle", return_value=Response()
            ),
        )
