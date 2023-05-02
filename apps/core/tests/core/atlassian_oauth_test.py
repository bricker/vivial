from http import HTTPStatus

from .base import BaseTestCase


class TestAtlassianOAuth(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    async def test_atlassian_authorize_endpoint(self) -> None:
        response = await self.make_request(
            "/oauth/atlassian/authorize",
            method="GET",
            payload={},
            follow_redirects=False,
        )

        assert response.status_code == HTTPStatus.TEMPORARY_REDIRECT
        assert response.is_redirect
        assert response.has_redirect_location
        self.assertRegex(response.headers["location"], r"https://auth\.atlassian\.com/authorize")
        assert response.cookies.get("ev_oauth_state_atlassian") is not None

    # async def test_atlassian_callback_endpoint(self) -> None:
    #     mockito.when2(eave.core.internal.oauth.atlassian.AtlassianOAuthSession.get_available_resources).thenReturn(
    #         [
    #             eave.core.internal.oauth.atlassian.AtlassianAvailableResource(
    #                 id=self.anystring("atlassian_cloud_id"),
    #                 url=self.anystring("confluence_document_response._links.base"),
    #                 avatarUrl=self.anystring("atlassianresourceavatar"),
    #                 name=self.anystring("atlassianresourcename"),
    #                 scopes=[],
    #             )
    #         ]
    #     )

    #     fake_token = {
    #         "access_token": self.anystring("oauth_access_token"),
    #         "expires_in": self.anyint("oauth_expires_in"),
    #         "scope": self.anystring("oauth_scope"),
    #     }

    #     mockito.when2(
    #         eave.core.internal.oauth.atlassian.AtlassianOAuthSession.fetch_token, code=self.anystring("oauthcode")
    #     ).thenReturn(fake_token)

    #     # Get the state cookie
    #     authorize_response = await self.make_request(
    #         "/oauth/atlassian/authorize",
    #         method="GET",
    #         follow_redirects=False,
    #     )

    #     self.assertEqual(authorize_response.status_code, HTTPStatus.TEMPORARY_REDIRECT)
    #     state = authorize_response.cookies.get("eave-oauth-state-atlassian")
    #     self.assertIsNotNone(state)

    #     async def get_installation() -> eave_orm.AtlassianInstallationOrm | None:
    #         installation = await eave_orm.AtlassianInstallationOrm.one_or_none_by_atlassian_cloud_id(
    #             session=self.dbsession,
    #             atlassian_cloud_id=self.anystring("atlassian_cloud_id"),
    #         )
    #         return installation

    #     installation = await get_installation()
    #     self.assertIsNone(installation)

    #     callback_response = await self.make_request(
    #         "/oauth/atlassian/callback",
    #         method="GET",
    #         payload={
    #             "state": state,
    #             "code": self.anystring("oauthcode"),
    #         },
    #     )

    #     self.assertEqual(callback_response.status_code, HTTPStatus.OK)

    #     installation = await get_installation()
    #     assert installation is not None
    #     self.assertEqual(installation.atlassian_cloud_id, self.anystring("atlassian_cloud_id"))
    #     self.assertEqual(installation.oauth_token_encoded, json.dumps(fake_token))
    #     # Test cookie was deleted
    #     self.assertIsNone(callback_response.cookies.get("eave-oauth-state-atlassian"))
