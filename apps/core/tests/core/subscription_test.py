import eave.core.internal.database as eave_db
import eave.core.internal.orm as eave_orm
import eave.stdlib.core_api.enums
import eave.stdlib.core_api.models as eave_models

from .base import BaseTestCase


class TestSubscriptionOrm(BaseTestCase):
    async def test_find_one(self) -> None:
        team = await self.make_team()

        subscription = eave_orm.SubscriptionOrm(
            team_id=team.id,
            source_platform=eave.stdlib.core_api.enums.SubscriptionSourcePlatform.slack,
            source_event=eave.stdlib.core_api.enums.SubscriptionSourceEvent.slack_message,
            source_id=self.anystring("source_id"),
        )
        await self.save(subscription)

        async with eave_db.get_async_session() as db_session:
            result = await eave_orm.SubscriptionOrm.one_or_none(
                session=db_session,
                team_id=team.id,
                source=eave_models.SubscriptionSource(
                    platform=eave.stdlib.core_api.enums.SubscriptionSourcePlatform.slack,
                    event=eave.stdlib.core_api.enums.SubscriptionSourceEvent.slack_message,
                    id=self.anystring("source_id"),
                ),
            )

        assert result is not None
        assert result.id == subscription.id
