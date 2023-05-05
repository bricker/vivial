from http import HTTPStatus
from typing import Optional
import pydantic

import eave.core.internal.database as eave_db
import eave.core.internal.orm.document_reference
import eave.stdlib.core_api.enums
from eave.core.internal.orm.subscription import SubscriptionOrm

from .base import BaseTestCase


class TestSubscriptionsEndpoints(BaseTestCase):
    async def _make_document(self) -> eave.core.internal.orm.document_reference.DocumentReferenceOrm:
        document_reference = eave.core.internal.orm.document_reference.DocumentReferenceOrm(
            team_id=self.team.id,
            document_id=self.anystring("confluence_document_response.id"),
            document_url=self.anystring("cdurl"),
        )
        return await self.save(document_reference)

    async def _make_subscription(self, document_reference_id: Optional[pydantic.UUID4] = None) -> SubscriptionOrm:
        subscription = SubscriptionOrm(
            team_id=self.team.id,
            source_platform=eave.stdlib.core_api.enums.SubscriptionSourcePlatform.slack,
            source_event=eave.stdlib.core_api.enums.SubscriptionSourceEvent.slack_message,
            source_id=self.anystring("source_id"),
            document_reference_id=document_reference_id,
        )
        return await self.save(subscription)

    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.team = await self.make_team()
        self.document_reference = await self._make_document()
        self.subscription = await self._make_subscription(document_reference_id=self.document_reference.id)

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
                "document_reference": {
                    "id": str(self.document_reference.id),
                },
            },
            team_id=self.team.id,
        )

        assert response.status_code == HTTPStatus.OK
        assert self.subscription.document_reference_id

        async with eave_db.async_session.begin() as db_session:
            subscription = await SubscriptionOrm.one_or_none(
                session=db_session,
                source=self.subscription.source,
                team_id=self.team.id,
                document_reference_id=self.subscription.document_reference_id,
            )

        assert subscription is None

    async def test_get_multiple_subscriptions(self) -> None:
        # create extra subscription in addition to one from setup,
        # but with different doc id (None here)
        await self._make_subscription()

        # make sure we get back both
        response = await self.make_request(
            "/subscriptions/query",
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
            team_id=self.team.id,
        )

        assert response.status_code == HTTPStatus.OK
        response_json = response.json()
        assert len(response_json["subscriptions"]) == 2
        assert len(response_json["subscriptions"]) == len(response_json["document_references"])

    async def test_get_noneexistent_subscription(self) -> None:
        response = await self.make_request(
            "/subscriptions/query",
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
                "document_reference": {
                    "id": self.anystring("nonexistent"),
                },
            },
            team_id=self.team.id,
        )

        assert response.status_code == HTTPStatus.OK
        response_json = response.json()
        assert len(response_json["subscriptions"]) == 0
        assert len(response_json["subscriptions"]) == len(response_json["document_references"])
