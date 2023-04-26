import os
from http import HTTPStatus

from .base import BaseTestCase


class TestStatusEndpoint(BaseTestCase):
    async def test_status_endpoint(self) -> None:
        os.environ["GAE_SERVICE"] = self.anystring("gaeservice")
        os.environ["GAE_VERSION"] = self.anystring("gaeversion")

        response = await self.httpclient.get("/status")
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {
            "status": "OK",
            "service": self.anystring("gaeservice"),
            "version": self.anystring("gaeversion"),
        }


# class TestAccessRequestEndpoint(BaseTestCase):
#     async def test_new_email(self) -> None:
#         response = await self.make_request(
#             "/access_request",
#             payload={"email": "bryan@bryan.com"},
#         )
#         self.assertEqual(response.status_code, HTTPStatus.CREATED)

#         access_request = await eave_orm.AccessRequestOrm.one_or_none(email="bryan@bryan.com", session=self.dbsession)
#         self.assertIsNotNone(access_request)

#     async def test_existing_email(self) -> None:
#         await self.make_request(
#             "/access_request",
#             payload={"email": "bryan@bryan.com"},
#         )

#         response = await self.make_request(
#             "/access_request",
#             payload={"email": "bryan@bryan.com"},
#         )

#         self.assertEqual(response.status_code, HTTPStatus.OK)

#         access_request = await eave_orm.AccessRequestOrm.one_or_none(email="bryan@bryan.com", session=self.dbsession)
#         self.assertIsNotNone(access_request)

#     async def test_visitor_id(self) -> None:
#         visitor_id = uuid4()
#         response = await self.make_request(
#             "/access_request",
#             payload={"email": "bryan@bryan.com", "visitor_id": str(visitor_id)},
#         )

#         self.assertEqual(response.status_code, HTTPStatus.CREATED)

#         access_request = await eave_orm.AccessRequestOrm.one_or_none(email="bryan@bryan.com", session=self.dbsession)
#         access_request = self.unwrap(access_request)
#         self.assertEqual(access_request.visitor_id, visitor_id)

#     async def test_duplicate_visitor_id(self) -> None:
#         visitor_id = uuid4()
#         response1 = await self.make_request(
#             "/access_request",
#             payload={"email": "bryan1@bryan.com", "visitor_id": str(visitor_id)},
#         )

#         self.assertEqual(response1.status_code, HTTPStatus.CREATED)

#         response2 = await self.make_request(
#             "/access_request",
#             payload={"email": "bryan2@bryan.com", "visitor_id": str(visitor_id)},
#         )

#         self.assertEqual(response2.status_code, HTTPStatus.CREATED)

#         access_request1 = await eave_orm.AccessRequestOrm.one_or_none(email="bryan1@bryan.com", session=self.dbsession)
#         access_request1 = self.unwrap(access_request1)
#         self.assertEqual(access_request1.visitor_id, visitor_id)

#         access_request2 = await eave_orm.AccessRequestOrm.one_or_none(email="bryan2@bryan.com", session=self.dbsession)
#         access_request2 = self.unwrap(access_request1)
#         self.assertEqual(access_request2.visitor_id, visitor_id)

#     async def test_bad_payload(self) -> None:
#         response = await self.make_request(
#             "/access_request",
#             payload={},
#         )
#         self.assertEqual(response.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)

#     async def test_invalid_email_format(self) -> None:
#         response = await self.make_request(
#             "/access_request",
#             payload={"email": "bad_email"},
#         )
#         self.assertEqual(response.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)

#     ## TODO: Test slack integration


# class TestDocumentsEndpoints(BaseTestCase):
#     async def asyncSetUp(self) -> None:
#         await super().asyncSetUp()

#         team = eave_orm.TeamOrm(
#             name=self.anystring("teamname"), document_platform=eave_models.DocumentPlatform.confluence
#         )
#         self._team = await self.save(team)

#         document_reference = eave_orm.DocumentReferenceOrm(
#             team_id=self._team.id,
#             document_id=self.anystring("confluence_document_response.id"),
#             document_url=self.anystring("cdurl"),
#         )
#         self._document_reference = await self.save(document_reference)

#         subscription = eave_orm.SubscriptionOrm(
#             team_id=team.id,
#             source_platform=eave_models.SubscriptionSourcePlatform.slack,
#             source_event=eave_models.SubscriptionSourceEvent.slack_message,
#             source_id=self.anystring("source_id"),
#         )
#         self._subscription = await self.save(subscription)

#     async def test_create_document_with_unique_title(self) -> None:
#         self.skipTest("wip")
#         # mockito.when2(Confluence.get_page_by_title, **mockito.KWARGS).thenReturn(None)
#         # mockito.when2(Confluence.create_page, **mockito.KWARGS).thenReturn(fixtures.confluence_document_response(self))

#         # response = await self.make_request(
#         #     "/documents/upsert",
#         #     headers={
#         #         "eave-team-id": str(self._team.id),
#         #     },
#         #     json={
#         #         "document": {"title": self.anystring("title"), "content": self.anystring("content")},
#         #         "subscription": {
#         #             "source": {
#         #                 "platform": self._subscription.source.platform,
#         #                 "event": self._subscription.source.event,
#         #                 "id": self._subscription.source.id,
#         #             },
#         #         },
#         #     },
#         # )

#         # self._subscription = await self.reload(self._subscription)
#         # document_reference = await self._subscription.get_document_reference(session=self.dbsession)
#         # document_reference = self.unwrap(document_reference)

#         # self.assertEqual(response.status_code, HTTPStatus.ACCEPTED)
#         # self.assertDictEqual(
#         #     response.json(),
#         #     {
#         #         "team": {
#         #             "id": str(self._team.id),
#         #             "name": self._team.name,
#         #             "document_platform": self._team.document_platform.value,
#         #         },
#         #         "subscription": {
#         #             "id": str(self._subscription.id),
#         #             "document_reference_id": str(document_reference.id),
#         #             "source": {
#         #                 "platform": self._subscription.source.platform.value,
#         #                 "event": self._subscription.source.event.value,
#         #                 "id": self._subscription.source.id,
#         #             },
#         #         },
#         #         "document_reference": {
#         #             "id": str(document_reference.id),
#         #             "document_url": document_reference.document_url,
#         #             "document_id": document_reference.document_id,
#         #         },
#         #     },
#         # )

#     async def test_create_document_with_duplicate_title(self) -> None:
#         self.skipTest("Not implemented")

#         # existing_document = fixtures.confluence_document_response(self)
#         # mockito.when2(Confluence.get_page_by_title, **mockito.KWARGS).thenReturn(existing_document)

#     async def test_update_document_with_missing_page(self) -> None:
#         """
#         Test what happens if the page was deleted
#         """
#         self.skipTest("Not implemented")
#         # mockito.when2(Confluence.get_page_by_id, **mockito.KWARGS).thenReturn(None)

#     async def test_update_document_with_existing_content(self) -> None:
#         existing_page = fixtures.confluence_document_response(self)

#         mockito.when2(Confluence.get_page_by_id, page_id=existing_page["id"], **mockito.KWARGS).thenReturn(
#             existing_page
#         )
#         mockito.when2(Confluence.update_page, page_id=existing_page["id"], **mockito.KWARGS).thenReturn(existing_page)
#         mockito.when2(eave.stdlib.openai_client.chat_completion, **mockito.KWARGS).thenReturn(
#             mock_coroutine(self.anystring("openairesponse"))
#         )

#         self._subscription.document_reference_id = self._document_reference.id
#         await self.save(self._subscription)

#         response = await self.make_request(
#             "/documents/upsert",
#             headers={
#                 "eave-team-id": str(self._team.id),
#             },
#             payload={
#                 "document": {"title": self.anystring("title"), "content": self.anystring("content")},
#                 "subscription": {
#                     "source": {
#                         "platform": self._subscription.source.platform,
#                         "event": self._subscription.source.event,
#                         "id": self._subscription.source.id,
#                     },
#                 },
#             },
#         )

#         mockito.verify(Confluence).update_page(
#             page_id=existing_page["id"],
#             title=existing_page["title"],  # testing that title wasn't changed
#             body=self.anystring("openairesponse"),  # testing that the openai response was used
#             representation="wiki",
#         )

#         self.assertEqual(response.status_code, HTTPStatus.ACCEPTED)
#         self.assertDictEqual(
#             response.json(),
#             {
#                 "team": {
#                     "id": str(self._team.id),
#                     "name": self._team.name,
#                     "document_platform": self._team.document_platform,
#                 },
#                 "subscription": {
#                     "id": str(self._subscription.id),
#                     "document_reference_id": str(self._document_reference.id),
#                     "source": {
#                         "platform": self._subscription.source.platform,
#                         "event": self._subscription.source.event,
#                         "id": self._subscription.source.id,
#                     },
#                 },
#                 "document_reference": {
#                     "id": str(self._document_reference.id),
#                     "document_url": self._document_reference.document_url,
#                     "document_id": self._document_reference.document_id,
#                 },
#             },
#         )

#     async def test_invalid_source_platform(self) -> None:
#         response = await self.make_request(
#             "/documents/upsert",
#             headers={
#                 "eave-team-id": str(self._team.id),
#             },
#             payload={
#                 "document": {"title": self.anystring("title"), "content": self.anystring("content")},
#                 "subscription": {
#                     "source": {
#                         "platform": "no",
#                         "event": self._subscription.source.event,
#                         "id": self._subscription.source.id,
#                     },
#                 },
#             },
#         )

#         self.assertEqual(response.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)
#         self.assertIsNotNone(response.json().get("detail"))

#     async def test_invalid_source_event(self) -> None:
#         response = await self.make_request(
#             "/documents/upsert",
#             headers={
#                 "eave-team-id": str(self._team.id),
#             },
#             payload={
#                 "document": {"title": self.anystring("title"), "content": self.anystring("content")},
#                 "subscription": {
#                     "source": {
#                         "platform": self._subscription.source.platform,
#                         "event": "no",
#                         "id": self._subscription.source.id,
#                     },
#                 },
#             },
#         )

#         self.assertEqual(response.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)
#         self.assertIsNotNone(response.json().get("detail"))

#     async def test_invalid_source_id(self) -> None:
#         response = await self.make_request(
#             "/documents/upsert",
#             headers={
#                 "eave-team-id": str(self._team.id),
#             },
#             payload={
#                 "document": {"title": self.anystring("title"), "content": self.anystring("content")},
#                 "subscription": {
#                     "source": {
#                         "platform": self._subscription.source.platform,
#                         "event": self._subscription.source.event,
#                         "id": "no",
#                     },
#                 },
#             },
#         )

#         self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
#         self.assertEqual(response.json(), {"detail": "Not Found"})

#     async def test_missing_document_content(self) -> None:
#         response = await self.make_request(
#             "/documents/upsert",
#             headers={
#                 "eave-team-id": str(self._team.id),
#             },
#             payload={
#                 "document": {},
#                 "subscription": {
#                     "source": {
#                         "platform": self._subscription.source.platform,
#                         "event": self._subscription.source.event,
#                         "id": self._subscription.source.id,
#                     },
#                 },
#             },
#         )

#         self.assertEqual(response.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)
#         self.assertIsNotNone(response.json()["detail"])

#     async def test_missing_document_attribute(self) -> None:
#         response = await self.make_request(
#             "/documents/upsert",
#             headers={
#                 "eave-team-id": str(self._team.id),
#             },
#             payload={
#                 "document": {
#                     "title": self.anystring(),
#                 },
#                 "subscription": {
#                     "source": {
#                         "platform": self._subscription.source.platform,
#                         "event": self._subscription.source.event,
#                         "id": self._subscription.source.id,
#                     },
#                 },
#             },
#         )

#         self.assertEqual(response.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)
#         self.assertIsNotNone(response.json()["detail"])

#     async def test_missing_team_header(self) -> None:
#         response = await self.make_request(
#             "/documents/upsert",
#             payload={
#                 "document": {"title": self.anystring("title"), "content": self.anystring("content")},
#                 "subscription": {
#                     "source": {
#                         "platform": self._subscription.source.platform,
#                         "event": self._subscription.source.event,
#                         "id": self._subscription.source.id,
#                     },
#                 },
#             },
#         )

#         self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
#         self.assertEqual(response.json(), {"detail": "Forbidden"})

#     async def test_invalid_team_id(self) -> None:
#         response = await self.make_request(
#             "/documents/upsert",
#             headers={"eave-team-id": str(uuid4())},
#             payload={
#                 "document": {
#                     "title": self.anystring("title"),
#                     "content": self.anystring("content"),
#                 },
#                 "subscription": {
#                     "source": {
#                         "platform": self._subscription.source.platform,
#                         "event": self._subscription.source.event,
#                         "id": self._subscription.source.id,
#                     },
#                 },
#             },
#         )

#         self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
