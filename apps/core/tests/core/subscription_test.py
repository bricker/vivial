import eave.core.internal.database as eave_db
from eave.core.internal.orm.subscription import SubscriptionOrm
import eave.stdlib.core_api.enums
import eave.stdlib.core_api.models as eave_models

from .base import BaseTestCase


class TestSubscriptionOrm(BaseTestCase):
    async def test_find_one(self) -> None:
        team = await self.make_team()

        subscription = SubscriptionOrm(
            team_id=team.id,
            source_platform=eave.stdlib.core_api.enums.SubscriptionSourcePlatform.slack,
            source_event=eave.stdlib.core_api.enums.SubscriptionSourceEvent.slack_message,
            source_id=self.anystring("source_id"),
        )
        await self.save(subscription)

        async with eave_db.async_session.begin() as db_session:
            result = await SubscriptionOrm.one_or_none(
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
