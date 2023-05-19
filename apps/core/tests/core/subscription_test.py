import eave.stdlib.core_api.enums
import eave.stdlib.core_api.models as eave_models

from eave.core.internal.orm.subscription import SubscriptionOrm
from pydantic import UUID4

from .base import BaseTestCase


class TestSubscriptionOrm(BaseTestCase):
    async def test_find_one(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)

            subscription = SubscriptionOrm(
                team_id=team.id,
                source_platform=eave.stdlib.core_api.enums.SubscriptionSourcePlatform.slack,
                source_event=eave.stdlib.core_api.enums.SubscriptionSourceEvent.slack_message,
                source_id=self.anystring("source_id"),
            )
            await self.save(s, subscription)

            result = await SubscriptionOrm.one_or_none(
                session=s,
                team_id=team.id,
                source=eave_models.SubscriptionSource(
                    platform=eave.stdlib.core_api.enums.SubscriptionSourcePlatform.slack,
                    event=eave.stdlib.core_api.enums.SubscriptionSourceEvent.slack_message,
                    id=self.anystring("source_id"),
                ),
            )

        assert result is not None
        assert result.id == subscription.id
