from http import HTTPStatus

import eave.core.internal.database as eave_db
import eave.core.internal.orm.document_reference
import eave.stdlib.core_api.enums
from eave.core.internal.orm.subscription import SubscriptionOrm

from .base import BaseTestCase


class TestSubscriptionsEndpoints(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        self.team = await self.make_team()

        document_reference = eave.core.internal.orm.document_reference.DocumentReferenceOrm(
            team_id=self.team.id,
            document_id=self.anystring("confluence_document_response.id"),
            document_url=self.anystring("cdurl"),
        )
        self.document_reference = await self.save(document_reference)

        subscription = SubscriptionOrm(
            team_id=self.team.id,
            source_platform=eave.stdlib.core_api.enums.SubscriptionSourcePlatform.slack,
            source_event=eave.stdlib.core_api.enums.SubscriptionSourceEvent.slack_message,
            source_id=self.anystring("source_id"),
        )
        self.subscription = await self.save(subscription)

    async def test_delete_subscription(self) -> None:
        response = await self.make_request(
            "/subscriptions/delete",
            headers={
                "eave-team-id": str(self.team.id),
            },
            payload={
                "subscription": {
                    "source": {
                        "platform": self.subscription.source.platform,
                        "event": self.subscription.source.event,
                        "id": self.subscription.source.id,
                    },
                },
            },
        )

        assert response.status_code == HTTPStatus.OK

        async with eave_db.async_session.begin() as db_session:
            subscription = await SubscriptionOrm.one_or_none(
                session=db_session, source=self.subscription.source, team_id=self.team.id
            )

        assert subscription is None
