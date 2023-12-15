from http import HTTPStatus
from eave.stdlib.core_api.models.subscriptions import SubscriptionInput, SubscriptionSource, SubscriptionSourceEvent, SubscriptionSourcePlatform
from eave.stdlib.core_api.operations.status import Status
from eave.stdlib.core_api.operations.subscriptions import CreateSubscriptionRequest

from eave.stdlib.headers import EAVE_TEAM_ID_HEADER

from .base import BaseTestCase


class TestTeamLookupMiddleware(BaseTestCase):
    async def test_team_id_bypass(self) -> None:
        response = await self.make_request(
            method=Status.config.method,
            path=Status.config.path,
            headers={EAVE_TEAM_ID_HEADER: None},
        )

        assert response.status_code == HTTPStatus.OK

    async def test_missing_team_id_header(self) -> None:
        response = await self.make_request(
            path=CreateSubscriptionRequest.config.path,
            payload=CreateSubscriptionRequest.RequestBody(
                subscription=SubscriptionInput(
                    source=SubscriptionSource(
                        platform=SubscriptionSourcePlatform.slack,
                        event=SubscriptionSourceEvent.slack_message,
                        id=self.anystring("source_id"),
                    ),
                ),
            ),
            headers={
                EAVE_TEAM_ID_HEADER: None,
            },
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST

    async def test_invalid_team_id(self) -> None:
        response = await self.make_request(
            path=CreateSubscriptionRequest.config.path,
            payload=CreateSubscriptionRequest.RequestBody(
                subscription=SubscriptionInput(
                    source=SubscriptionSource(
                        platform=SubscriptionSourcePlatform.slack,
                        event=SubscriptionSourceEvent.slack_message,
                        id=self.anystring("source_id"),
                    ),
                ),
            ),
            headers={
                EAVE_TEAM_ID_HEADER: None,
            },
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST
