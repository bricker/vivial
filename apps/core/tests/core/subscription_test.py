from uuid import uuid4

import eave.core.internal.orm as eave_orm
import eave.stdlib.core_api.models as eave_models
from .base import BaseTestCase


class TestSubscritionOrm(BaseTestCase):
    async def test_find_one(self) -> None:
        team = eave_orm.TeamOrm(name="Test Org", document_platform=eave_models.DocumentPlatform.confluence)
        self.dbsession.add(team)
        await self.dbsession.commit()

        test_id = uuid4()
        subscription = eave_orm.SubscriptionOrm(
            team_id=team.id,
            source_platform=eave_models.SubscriptionSourcePlatform.slack,
            source_event=eave_models.SubscriptionSourceEvent.slack_message,
            source_id=str(test_id),
        )
        self.dbsession.add(subscription)
        await self.dbsession.commit()

        result = await eave_orm.SubscriptionOrm.one_or_none(
            session=self.dbsession,
            team_id=team.id,
            source=eave_models.SubscriptionSource(
                platform=eave_models.SubscriptionSourcePlatform.slack, event=eave_models.SubscriptionSourceEvent.slack_message, id=str(test_id)
            ),
        )
        result = self.unwrap(result)
        self.assertEqual(result, subscription)
