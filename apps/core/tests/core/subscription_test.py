# from uuid import uuid4

# import eave.core.internal.orm as orm
# import tests
# from eave.core.public.shared import (
#     DocumentPlatform,
#     SubscriptionSource,
#     SubscriptionSourceEvent,
#     SubscriptionSourcePlatform,
# )
# from tests.base import BaseTestCase


# class TestSubscritionOrm(BaseTestCase):
#     async def test_find_one(self) -> None:
#         team = orm.TeamOrm(name="Test Org", document_platform=DocumentPlatform.confluence)
#         self.dbsession.add(team)
#         await self.dbsession.commit()

#         test_id = uuid4()
#         subscription = orm.SubscriptionOrm(
#             team_id=team.id,
#             source_platform=SubscriptionSourcePlatform.slack,
#             source_event=SubscriptionSourceEvent.slack_message,
#             source_id=str(test_id),
#         )
#         self.dbsession.add(subscription)
#         await self.dbsession.commit()

#         result = await orm.SubscriptionOrm.one_or_none(
#             session=self.dbsession,
#             team_id=team.id,
#             source=SubscriptionSource(
#                 platform=SubscriptionSourcePlatform.slack, event=SubscriptionSourceEvent.slack_message, id=str(test_id)
#             ),
#         )
#         result = self.unwrap(result)
#         self.assertEqual(result, subscription)
