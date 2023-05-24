import http

from eave.core.internal.orm.atlassian_installation import AtlassianInstallationOrm
from eave.core.internal.orm.document_reference import DocumentReferenceOrm
from eave.core.internal.orm.subscription import SubscriptionOrm
from eave.stdlib.core_api.enums import SubscriptionSourceEvent, SubscriptionSourcePlatform
from eave.stdlib.core_api.models import SubscriptionSource
from .base import BaseTestCase


class TestDeleteDocument(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        async with self.db_session.begin() as s:
            self.testdata["eave_team"] = eave_team = await self.make_team(s)
            await AtlassianInstallationOrm.create(
                session=s,
                atlassian_cloud_id=self.anystring("atlassian_cloud_id"),
                confluence_space_key=self.anystring("confluence_space_key"),
                oauth_token_encoded=self.anyjson("oauth_token_encoded"),
                team_id=eave_team.id,
            )

    async def test_delete(self) -> None:
        async with self.db_session.begin() as s:
            document_reference = await DocumentReferenceOrm.create(
                session=s,
                team_id=self.testdata["eave_team"].id,
                document_id=str(self.anyint("document id")),
                document_url=self.anystring("document url"),
            )

            await SubscriptionOrm.create(
                session=s,
                team_id=self.testdata["eave_team"].id,
                source=SubscriptionSource(
                    platform=SubscriptionSourcePlatform.slack,
                    event=SubscriptionSourceEvent.slack_message,
                    id=self.anystring(),
                ),
                document_reference_id=document_reference.id,
            )

            await SubscriptionOrm.create(
                session=s,
                team_id=self.testdata["eave_team"].id,
                source=SubscriptionSource(
                    platform=SubscriptionSourcePlatform.slack,
                    event=SubscriptionSourceEvent.slack_message,
                    id=self.anystring(),
                ),
                document_reference_id=document_reference.id,
            )

            subs = await SubscriptionOrm.select(
                session=s, team_id=self.testdata["eave_team"].id, document_reference_id=document_reference.id
            )
            assert len(subs) == 2

        mock = self.get_mock("AtlassianRestAPI.post")

        response = await self.make_request(
            path="/documents/delete",
            payload={
                "document_reference": {
                    "id": str(document_reference.id),
                }
            },
            team_id=self.testdata["eave_team"].id,
        )

        assert response.status_code == http.HTTPStatus.OK
        assert mock.call_count == 1

        async with self.db_session.begin() as s:
            after = await DocumentReferenceOrm.one_or_none(
                session=s, team_id=self.testdata["eave_team"].id, id=document_reference.id
            )
            assert after is None

            subs = await SubscriptionOrm.select(
                session=s, team_id=self.testdata["eave_team"].id, document_reference_id=document_reference.id
            )
            assert len(subs) == 0
