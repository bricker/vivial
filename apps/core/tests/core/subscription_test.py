from uuid import uuid4

import eave.stdlib.core_api.enums

import eave.core.internal.orm as eave_orm
import eave.stdlib.core_api.models as eave_models

from .base import BaseTestCase


class TestSubscritionOrm(BaseTestCase):
    async def test_find_one(self) -> None:
        team = eave_orm.TeamOrm(name="Test Org", document_platform=eave.stdlib.core_api.enums.DocumentPlatform.confluence)
        self.db_session.add(team)
        await self.db_session.commit()

        test_id = uuid4()
        subscription = eave_orm.SubscriptionOrm(
            team_id=team.id,
            source_platform=eave.stdlib.core_api.enums.SubscriptionSourcePlatform.slack,
            source_event=eave.stdlib.core_api.enums.SubscriptionSourceEvent.slack_message,
            source_id=str(test_id),
        )
        self.db_session.add(subscription)
        await self.db_session.commit()

        result = await eave_orm.SubscriptionOrm.one_or_none(
            session=self.db_session,
            team_id=team.id,
            source=eave_models.SubscriptionSource(
                platform=eave.stdlib.core_api.enums.SubscriptionSourcePlatform.slack,
                event=eave.stdlib.core_api.enums.SubscriptionSourceEvent.slack_message,
                id=str(test_id),
            ),
        )
        result = self.unwrap(result)
        self.assertEqual(result, subscription)
