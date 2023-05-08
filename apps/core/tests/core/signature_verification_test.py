from http import HTTPStatus

from .base import BaseTestCase


class TestSignatureVerification(BaseTestCase):
    async def test_signature_bypass(self) -> None:
        response = await self.make_request(
            method="GET",
            path="/status",
            headers={"eave-signature": None},
        )

        assert response.status_code == HTTPStatus.OK
        assert self.get_mock("eave.stdlib.signing.verify_signature_or_exception").call_count == 0

    async def test_missing_signature_header(self) -> None:
        response = await self.make_request(
            path="/integrations/slack/query",
            headers={
                "eave-signature": None,
            },
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert self.get_mock("eave.stdlib.signing.verify_signature_or_exception").call_count == 0

    async def test_mismatched_signature(self) -> None:
        response = await self.make_request(
            path="/integrations/slack/query",
            headers={
                "eave-signature": "sdfdsfs",
            },
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert self.get_mock("eave.stdlib.signing.verify_signature_or_exception").call_count == 1

    async def test_signature_with_team_id(self) -> None:
        team = await self.make_team()
        response = await self.make_request(
            path="/subscriptions/create",
            payload={
                "subscription": {
                    "source": {
                        "platform": "slack",
                        "event": "slack_message",
                        "id": self.anystring("source_id"),
                    },
                },
            },
            headers={
                "eave-team-id": str(team.id),
            },
        )

        assert response.status_code == HTTPStatus.CREATED
        assert self.get_mock("eave.stdlib.signing.verify_signature_or_exception").call_count == 1
