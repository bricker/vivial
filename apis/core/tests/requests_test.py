from http import HTTPStatus
from uuid import UUID, uuid4

import mockito
import mockito.matchers
from atlassian import Confluence

import eave.internal.openai
import eave.internal.orm as orm
import tests
from eave.public.shared import (
    DocumentPlatform,
    SubscriptionSourceEvent,
    SubscriptionSourcePlatform,
)
from tests import fixtures
from tests.base import BaseTestCase, mock_coroutine


class TestStatusEndpoint(BaseTestCase):
    async def test_status(self) -> None:
        response = await self.httpclient.get("/status")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.json(), {"status": "1", "service": "api"})

class TestAccessRequestEndpoint(BaseTestCase):
    async def test_new_email(self) -> None:
        response = await self.httpclient.post(
            "/access_request",
            json={"email": "bryan@bryan.com"},
        )
        self.assertEqual(response.status_code, HTTPStatus.CREATED)

        access_request = await orm.AccessRequestOrm.find_one(email="bryan@bryan.com", session=self.dbsession)
        self.assertIsNotNone(access_request)

    async def test_existing_email(self) -> None:
        await self.httpclient.post(
            "/access_request",
            json={"email": "bryan@bryan.com"},
        )

        response = await self.httpclient.post(
            "/access_request",
            json={"email": "bryan@bryan.com"},
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)

        access_request = await orm.AccessRequestOrm.find_one(email="bryan@bryan.com", session=self.dbsession)
        self.assertIsNotNone(access_request)

    async def test_visitor_id(self) -> None:
        visitor_id = uuid4()
        response = await self.httpclient.post(
            "/access_request",
            json={"email": "bryan@bryan.com", "visitor_id": str(visitor_id)},
        )

        self.assertEqual(response.status_code, HTTPStatus.CREATED)

        access_request = await orm.AccessRequestOrm.find_one(email="bryan@bryan.com", session=self.dbsession)
        access_request = self.unwrap(access_request)
        self.assertEqual(access_request.visitor_id, visitor_id)

    async def test_duplicate_visitor_id(self) -> None:
        visitor_id = uuid4()
        response1 = await self.httpclient.post(
            "/access_request",
            json={"email": "bryan1@bryan.com", "visitor_id": str(visitor_id)},
        )

        self.assertEqual(response1.status_code, HTTPStatus.CREATED)

        response2 = await self.httpclient.post(
            "/access_request",
            json={"email": "bryan2@bryan.com", "visitor_id": str(visitor_id)},
        )

        self.assertEqual(response2.status_code, HTTPStatus.CREATED)

        access_request1 = await orm.AccessRequestOrm.find_one(email="bryan1@bryan.com", session=self.dbsession)
        access_request1 = self.unwrap(access_request1)
        self.assertEqual(access_request1.visitor_id, visitor_id)

        access_request2 = await orm.AccessRequestOrm.find_one(email="bryan2@bryan.com", session=self.dbsession)
        access_request2 = self.unwrap(access_request1)
        self.assertEqual(access_request2.visitor_id, visitor_id)

    async def test_bad_payload(self) -> None:
        response = await self.httpclient.post(
            "/access_request",
            json={},
        )
        self.assertEqual(response.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)

    async def test_invalid_email_format(self) -> None:
        response = await self.httpclient.post(
            "/access_request",
            json={"email": "bad_email"},
        )
        self.assertEqual(response.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)

    ## TODO: Test slack integration


class TestDocumentsEndpoints(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        team = orm.TeamOrm(name=self.anystring("teamname"), document_platform=DocumentPlatform.confluence)
        self._team = await self.save(team)

        confluence_destination = orm.ConfluenceDestinationOrm(
            team_id=team.id,
            url="https://eave-fyi.atlassian.org",
            api_username="eave",
            api_key="xxx",
            space="EAVE",
        )
        self._confluence_destination = await self.save(confluence_destination)

        document_reference = orm.DocumentReferenceOrm(
            team_id=self._team.id,
            document_id=self.anystring("confluence_document_response.id"),
            document_url=self.anystring("cdurl"),
        )
        self._document_reference = await self.save(document_reference)

        subscription = orm.SubscriptionOrm(
            team_id=team.id,
            source_platform=SubscriptionSourcePlatform.slack,
            source_event=SubscriptionSourceEvent.slack_message,
            source_id=self.anystring("source_id"),
        )
        self._subscription = await self.save(subscription)

    async def test_create_document_with_unique_title(self) -> None:
        self.skipTest("wip")
        # mockito.when2(Confluence.get_page_by_title, **mockito.KWARGS).thenReturn(None)
        # mockito.when2(Confluence.create_page, **mockito.KWARGS).thenReturn(fixtures.confluence_document_response(self))

        # response = await self.httpclient.post(
        #     "/documents/upsert",
        #     headers={
        #         "eave-team-id": str(self._team.id),
        #     },
        #     json={
        #         "document": {"title": self.anystring("title"), "content": self.anystring("content")},
        #         "subscription": {
        #             "source": {
        #                 "platform": self._subscription.source.platform,
        #                 "event": self._subscription.source.event,
        #                 "id": self._subscription.source.id,
        #             },
        #         },
        #     },
        # )

        # self._subscription = await self.reload(self._subscription)
        # document_reference = await self._subscription.get_document_reference(session=self.dbsession)
        # document_reference = self.unwrap(document_reference)

        # self.assertEqual(response.status_code, HTTPStatus.ACCEPTED)
        # self.assertDictEqual(
        #     response.json(),
        #     {
        #         "team": {
        #             "id": str(self._team.id),
        #             "name": self._team.name,
        #             "document_platform": self._team.document_platform.value,
        #         },
        #         "subscription": {
        #             "id": str(self._subscription.id),
        #             "document_reference_id": str(document_reference.id),
        #             "source": {
        #                 "platform": self._subscription.source.platform.value,
        #                 "event": self._subscription.source.event.value,
        #                 "id": self._subscription.source.id,
        #             },
        #         },
        #         "document_reference": {
        #             "id": str(document_reference.id),
        #             "document_url": document_reference.document_url,
        #             "document_id": document_reference.document_id,
        #         },
        #     },
        # )

    async def test_create_document_with_duplicate_title(self) -> None:
        self.skipTest("Not implemented")

        # existing_document = fixtures.confluence_document_response(self)
        # mockito.when2(Confluence.get_page_by_title, **mockito.KWARGS).thenReturn(existing_document)

    async def test_update_document_with_missing_page(self) -> None:
        """
        Test what happens if the page was deleted
        """
        self.skipTest("Not implemented")
        # mockito.when2(Confluence.get_page_by_id, **mockito.KWARGS).thenReturn(None)

    async def test_update_document_with_existing_content(self) -> None:
        existing_page = fixtures.confluence_document_response(self)

        mockito.when2(Confluence.get_page_by_id, page_id=existing_page["id"], **mockito.KWARGS).thenReturn(
            existing_page
        )
        mockito.when2(Confluence.update_page, page_id=existing_page["id"], **mockito.KWARGS).thenReturn(existing_page)
        mockito.when2(eave.internal.openai.summarize, **mockito.KWARGS).thenReturn(
            mock_coroutine(self.anystring("openairesponse"))
        )

        self._subscription.document_reference_id = self._document_reference.id
        await self.save(self._subscription)

        response = await self.httpclient.post(
            "/documents/upsert",
            headers={
                "eave-team-id": str(self._team.id),
            },
            json={
                "document": {"title": self.anystring("title"), "content": self.anystring("content")},
                "subscription": {
                    "source": {
                        "platform": self._subscription.source.platform,
                        "event": self._subscription.source.event,
                        "id": self._subscription.source.id,
                    },
                },
            },
        )

        mockito.verify(Confluence).update_page(
            page_id=existing_page["id"],
            title=existing_page["title"],  # testing that title wasn't changed
            body=self.anystring("openairesponse"),  # testing that the openai response was used
            representation="wiki",
        )

        self.assertEqual(response.status_code, HTTPStatus.ACCEPTED)
        self.assertDictEqual(
            response.json(),
            {
                "team": {
                    "id": str(self._team.id),
                    "name": self._team.name,
                    "document_platform": self._team.document_platform.value,
                },
                "subscription": {
                    "id": str(self._subscription.id),
                    "document_reference_id": str(self._document_reference.id),
                    "source": {
                        "platform": self._subscription.source.platform,
                        "event": self._subscription.source.event,
                        "id": self._subscription.source.id,
                    },
                },
                "document_reference": {
                    "id": str(self._document_reference.id),
                    "document_url": self._document_reference.document_url,
                    "document_id": self._document_reference.document_id,
                },
            },
        )

    async def test_invalid_source_platform(self) -> None:
        response = await self.httpclient.post(
            "/documents/upsert",
            headers={
                "eave-team-id": str(self._team.id),
            },
            json={
                "document": {"title": self.anystring("title"), "content": self.anystring("content")},
                "subscription": {
                    "source": {
                        "platform": "no",
                        "event": self._subscription.source.event,
                        "id": self._subscription.source.id,
                    },
                },
            },
        )

        self.assertEqual(response.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)
        self.assertIsNotNone(response.json().get("detail"))

    async def test_invalid_source_event(self) -> None:
        response = await self.httpclient.post(
            "/documents/upsert",
            headers={
                "eave-team-id": str(self._team.id),
            },
            json={
                "document": {"title": self.anystring("title"), "content": self.anystring("content")},
                "subscription": {
                    "source": {
                        "platform": self._subscription.source.platform,
                        "event": "no",
                        "id": self._subscription.source.id,
                    },
                },
            },
        )

        self.assertEqual(response.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)
        self.assertIsNotNone(response.json().get("detail"))

    async def test_invalid_source_id(self) -> None:
        response = await self.httpclient.post(
            "/documents/upsert",
            headers={
                "eave-team-id": str(self._team.id),
            },
            json={
                "document": {"title": self.anystring("title"), "content": self.anystring("content")},
                "subscription": {
                    "source": {
                        "platform": self._subscription.source.platform,
                        "event": self._subscription.source.event,
                        "id": "no",
                    },
                },
            },
        )

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(response.json(), {"detail": "Not Found"})

    async def test_missing_document_content(self) -> None:
        response = await self.httpclient.post(
            "/documents/upsert",
            headers={
                "eave-team-id": str(self._team.id),
            },
            json={
                "document": {},
                "subscription": {
                    "source": {
                        "platform": self._subscription.source.platform,
                        "event": self._subscription.source.event,
                        "id": self._subscription.source.id,
                    },
                },
            },
        )

        self.assertEqual(response.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)
        self.assertIsNotNone(response.json()["detail"])

    async def test_missing_document_attribute(self) -> None:
        response = await self.httpclient.post(
            "/documents/upsert",
            headers={
                "eave-team-id": str(self._team.id),
            },
            json={
                "document": {
                    "title": self.anystring(),
                },
                "subscription": {
                    "source": {
                        "platform": self._subscription.source.platform,
                        "event": self._subscription.source.event,
                        "id": self._subscription.source.id,
                    },
                },
            },
        )

        self.assertEqual(response.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)
        self.assertIsNotNone(response.json()["detail"])

    async def test_missing_team_header(self) -> None:
        response = await self.httpclient.post(
            "/documents/upsert",
            headers=None,
            json={
                "document": {"title": self.anystring("title"), "content": self.anystring("content")},
                "subscription": {
                    "source": {
                        "platform": self._subscription.source.platform,
                        "event": self._subscription.source.event,
                        "id": self._subscription.source.id,
                    },
                },
            },
        )

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertEqual(response.json(), {"detail": "Forbidden"})

    async def test_invalid_team_id(self) -> None:
        response = await self.httpclient.post(
            "/documents/upsert",
            headers={"eave-team-id": str(uuid4())},
            json={
                "document": {
                    "title": self.anystring("title"),
                    "content": self.anystring("content"),
                },
                "subscription": {
                    "source": {
                        "platform": self._subscription.source.platform,
                        "event": self._subscription.source.event,
                        "id": self._subscription.source.id,
                    },
                },
            },
        )

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
