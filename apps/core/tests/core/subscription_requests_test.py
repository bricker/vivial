from http import HTTPStatus

import eave.core.internal.orm as orm
import eave.stdlib.core_api.models as eave_models

from .base import BaseTestCase


class TestSubscriptionsEndpoints(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        team = orm.TeamOrm(name=self.anystring("teamname"), document_platform=eave_models.DocumentPlatform.confluence)
        self._team = await self.save(team)

        document_reference = orm.DocumentReferenceOrm(
            team_id=self._team.id,
            document_id=self.anystring("confluence_document_response.id"),
            document_url=self.anystring("cdurl"),
        )
        self._document_reference = await self.save(document_reference)

        subscription = orm.SubscriptionOrm(
            team_id=self._team.id,
            source_platform=eave_models.SubscriptionSourcePlatform.slack,
            source_event=eave_models.SubscriptionSourceEvent.slack_message,
            source_id=self.anystring("source_id"),
        )
        self._subscription = await self.save(subscription)

    async def test_delete_subscription(self) -> None:
        response = await self.make_request(
            "/subscriptions/delete",
            headers={
                "eave-team-id": str(self._team.id),
            },
            payload={
                "subscription": {
                    "source": {
                        "platform": self._subscription.source.platform,
                        "event": self._subscription.source.event,
                        "id": self._subscription.source.id,
                    },
                },
            },
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        subscription = await orm.SubscriptionOrm.one_or_none(
            session=self.dbsession, source=self._subscription.source, team_id=self._team.id
        )

        self.assertEqual(subscription, None)
