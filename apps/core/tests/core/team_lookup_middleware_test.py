from http import HTTPStatus

from .base import BaseTestCase


class TestTeamLookupMiddleware(BaseTestCase):
    async def test_team_id_bypass(self) -> None:
        response = await self.make_request(
            method="GET",
            path="/status",
            headers={"eave-team-id": None},
        )

        assert response.status_code == HTTPStatus.OK

    async def test_missing_team_id_header(self) -> None:
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
                "eave-team-id": None,
            },
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST

    async def test_invalid_team_id(self) -> None:
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
                "eave-team-id": None,
            },
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST
