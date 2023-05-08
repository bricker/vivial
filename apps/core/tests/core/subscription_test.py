import eave.stdlib.core_api.enums
import eave.stdlib.core_api.models as eave_models

import eave.core.internal.database as eave_db
from eave.core.internal.orm.subscription import SubscriptionOrm
from pydantic import UUID4

from .base import BaseTestCase


class TestSubscriptionOrm(BaseTestCase):
    async def test_find_one(self) -> None:
        team = await self.make_team()
        doc_id = UUID4("7b1b3e6a-5a28-4e14-9cad-4a3cbebeee2c")

        subscription = SubscriptionOrm(
            team_id=team.id,
            source_platform=eave.stdlib.core_api.enums.SubscriptionSourcePlatform.slack,
            source_event=eave.stdlib.core_api.enums.SubscriptionSourceEvent.slack_message,
            source_id=self.anystring("source_id"),
            document_reference_id=doc_id,
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
