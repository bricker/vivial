import http
import unittest.mock

from eave.core.internal.orm.atlassian_installation import AtlassianInstallationOrm
from eave.core.internal.orm.confluence_destination import ConfluenceDestinationOrm
from eave.core.internal.orm.connect_installation import ConnectInstallationOrm
from eave.core.internal.orm.document_reference import DocumentReferenceOrm
from eave.core.internal.orm.subscription import SubscriptionOrm
from eave.stdlib.core_api.models.connect import AtlassianProduct, RegisterConnectInstallationInput
from eave.stdlib.core_api.models.subscriptions import SubscriptionSourceEvent, SubscriptionSourcePlatform
from eave.stdlib.core_api.models.subscriptions import SubscriptionSource
from .base import BaseTestCase


class TestDeleteDocument(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        async with self.db_session.begin() as s:
            self.testdata["eave_team"] = await self.make_team(s)
            connect = await ConnectInstallationOrm.create(
                session=s,
                team_id=self.testdata["eave_team"].id,
                input=RegisterConnectInstallationInput.parse_obj({
                    "product": AtlassianProduct.confluence,
                    "client_key": self.anystring("client_key"),
                    "base_url": self.anystring("base_url"),
                    "shared_secret": self.anystring("shared_secret"),
                }),
            )

            await ConfluenceDestinationOrm.create(
                session=s,
                connect_installation_id=connect.id,
                team_id=self.testdata["eave_team"].id,
                space_key=self.anystring("space_key"),
            )

            self._request_mock = self.patch(
                name="DeleteContentRequest",
                patch=unittest.mock.patch('eave.stdlib.confluence_api.operations.DeleteContentRequest.perform')
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

            subs = await SubscriptionOrm.query(
                session=s, team_id=self.testdata["eave_team"].id, document_reference_id=document_reference.id
            )
            assert len(subs) == 2

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
        assert self._request_mock.call_count == 1

        async with self.db_session.begin() as s:
            after = await DocumentReferenceOrm.one_or_none(
                session=s, team_id=self.testdata["eave_team"].id, id=document_reference.id
            )
            assert after is None

            subs = await SubscriptionOrm.query(
                session=s, team_id=self.testdata["eave_team"].id, document_reference_id=document_reference.id
            )
            assert len(subs) == 0
