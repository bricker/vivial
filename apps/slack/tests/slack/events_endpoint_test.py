import http
import unittest.mock

from eave.stdlib.headers import GCP_CLOUD_TRACE_CONTEXT, GCP_GAE_REQUEST_LOG_ID
from .base import BaseTestCase


class EventsEndpointTest(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.patch(
            name="CloudTasksAsyncClient.create_task",
            patch=unittest.mock.patch("eave.stdlib.task_queue.tasks.CloudTasksAsyncClient.create_task", autospec=True),
        )

    async def test_ssl_check(self) -> None:
        response = await self.httpclient.request(
            "POST",
            "/slack/events",
            json={"ssl_check": "1"},
        )

        assert response.status_code == http.HTTPStatus.OK
        assert self.get_mock("CloudTasksAsyncClient.create_task").call_count == 0

    async def test_url_verification(self) -> None:
        response = await self.httpclient.request(
            "POST",
            "/slack/events",
            json={"type": "url_verification", "challenge": self.anystring("slack challenge")},
        )

        assert response.status_code == http.HTTPStatus.OK
        assert response.json()["challenge"] == self.anystring("slack challenge")
        assert self.get_mock("CloudTasksAsyncClient.create_task").call_count == 0

    async def test_invalid_signature(self) -> None:
        response = await self.httpclient.request(
            "POST",
            "/slack/events",
            headers={**self._signature_headers()},
            json={**self._standard_body_fields()},
        )

        assert response.status_code == http.HTTPStatus.OK
        assert self.get_mock("CloudTasksAsyncClient.create_task").call_count == 0

    async def test_not_watched_event(self) -> None:
        self._patch_signature_verification()

        response = await self.httpclient.request(
            "POST",
            "/slack/events",
            headers={**self._signature_headers()},
            json={**self._standard_body_fields(), "event": {"type": "file_deleted"}},
        )

        assert response.status_code == http.HTTPStatus.OK
        assert self.get_mock("CloudTasksAsyncClient.create_task").call_count == 0

    async def test_valid_event(self) -> None:
        self._patch_signature_verification()

        response = await self.httpclient.request(
            "POST",
            "/slack/events",
            headers={**self._signature_headers(), GCP_GAE_REQUEST_LOG_ID: self.anystring(GCP_GAE_REQUEST_LOG_ID)},
            json={**self._standard_body_fields(), "event": {"type": "message"}},
        )

        assert response.status_code == http.HTTPStatus.OK

        mock = self.get_mock("CloudTasksAsyncClient.create_task")
        assert mock.call_count == 1

        task_arg = mock.mock_calls[0].kwargs["task"]
        # This is probably unnecessarily specific
        assert task_arg.name, (
            "projects/eavefyi-dev"
            "/locations/us-central1"
            "/queues/slack-events-processor"
            "/tasks/{}-{}".format(self.anystring("slack team ID"), self.anystring(GCP_GAE_REQUEST_LOG_ID))
        )

        assert "eave-signature" in task_arg.app_engine_http_request.headers
        assert "eave-origin" in task_arg.app_engine_http_request.headers
        assert "eave-request-id" in task_arg.app_engine_http_request.headers

    async def test_valid_event_with_trace_context_header(self) -> None:
        self._patch_signature_verification()

        response = await self.httpclient.request(
            "POST",
            "/slack/events",
            headers={**self._signature_headers(), GCP_CLOUD_TRACE_CONTEXT: self.anystring(GCP_CLOUD_TRACE_CONTEXT)},
            json={**self._standard_body_fields(), "event": {"type": "message"}},
        )

        assert response.status_code == http.HTTPStatus.OK

        mock = self.get_mock("CloudTasksAsyncClient.create_task")
        assert mock.call_count == 1

        # This is probably unnecessarily specific
        assert mock.mock_calls[0].kwargs["task"].name, (
            "projects/eavefyi-dev"
            "/locations/us-central1"
            "/queues/slack-events-processor"
            "/tasks/{}-{}".format(self.anystring("slack team ID"), self.anystring(GCP_CLOUD_TRACE_CONTEXT))
        )

    def _patch_signature_verification(self) -> None:
        self.patch(
            name="signature check",
            patch=unittest.mock.patch(
                "eave.slack.requests.event_callback.SignatureVerifier.is_valid_request", return_value=True
            ),
        )

    def _signature_headers(self) -> dict[str, str]:
        return {
            "x-slack-signature": self.anystring("slack signature"),
            "x-slack-request-timestamp": str(self.anyint()),
        }

    def _standard_body_fields(self) -> dict[str, str]:
        return {"team_id": self.anystring("slack team ID"), "type": "event_callback"}
