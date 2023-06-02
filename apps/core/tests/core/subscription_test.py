from eave.core.internal.orm.document_reference import DocumentReferenceOrm

from eave.core.internal.orm.subscription import SubscriptionOrm
from eave.stdlib.core_api.models.subscriptions import SubscriptionSourceEvent, SubscriptionSourcePlatform
from eave.stdlib.core_api.models.subscriptions import SubscriptionSource

from .base import BaseTestCase


class TestSubscriptionOrm(BaseTestCase):
    async def test_find_one(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)

            subscription = SubscriptionOrm(
                team_id=team.id,
                source_platform=SubscriptionSourcePlatform.slack,
                source_event=SubscriptionSourceEvent.slack_message,
                source_id=self.anystring("source_id"),
            )
            await self.save(s, subscription)

            result = await SubscriptionOrm.one_or_none(
                session=s,
                team_id=team.id,
                source=SubscriptionSource(
                    platform=SubscriptionSourcePlatform.slack,
                    event=SubscriptionSourceEvent.slack_message,
                    id=self.anystring("source_id"),
                ),
            )

        assert result is not None
        assert result.id == subscription.id

    async def test_select_with_document_reference_id(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)

            document_reference = await DocumentReferenceOrm.create(
                session=s,
                team_id=team.id,
                document_id=self.anystring(),
                document_url=self.anystring(),
            )

            await SubscriptionOrm.create(
                session=s,
                team_id=team.id,
                source=SubscriptionSource(
                    platform=SubscriptionSourcePlatform.slack,
                    event=SubscriptionSourceEvent.slack_message,
                    id=self.anystring(),
                ),
                document_reference_id=document_reference.id,
            )

            result = await SubscriptionOrm.query(
                session=s, team_id=team.id, document_reference_id=document_reference.id
            )
            assert len(result) == 1
            assert result[0].document_reference_id == document_reference.id

    async def test_select_with_source(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)

            source = SubscriptionSource(
                platform=SubscriptionSourcePlatform.slack,
                event=SubscriptionSourceEvent.slack_message,
                id=self.anystring("source id"),
            )
            await SubscriptionOrm.create(
                session=s,
                team_id=team.id,
                source=source,
            )

            result = await SubscriptionOrm.query(session=s, team_id=team.id, source=source)
            assert len(result) == 1
            assert result[0].source_id == self.getstr("source id")

    async def test_select_with_id(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)

            source = SubscriptionSource(
                platform=SubscriptionSourcePlatform.slack,
                event=SubscriptionSourceEvent.slack_message,
                id=self.anystring("source id"),
            )
            sub = await SubscriptionOrm.create(
                session=s,
                team_id=team.id,
                source=source,
            )

            result = await SubscriptionOrm.query(session=s, team_id=team.id, id=sub.id)
            assert len(result) == 1
            assert result[0].id == sub.id
