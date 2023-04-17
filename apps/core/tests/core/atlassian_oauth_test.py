from http import HTTPStatus
import json
import mockito
import eave.core.internal.orm as eave_orm
import eave.stdlib.core_api.models as eave_models
import eave.core.internal.oauth.atlassian
from .base import BaseTestCase


class TestAtlassianOAuth(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        team = eave_orm.TeamOrm(name=self.anystring("teamname"), document_platform=eave_models.DocumentPlatform.confluence)
        self._team = await self.save(team)

    async def test_atlassian_authorize_endpoint(self) -> None:
        response = await self.make_request(
            "/oauth/atlassian/authorize",
            method="GET",
            payload={},
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, HTTPStatus.TEMPORARY_REDIRECT)
        self.assertTrue(response.is_redirect)
        self.assertTrue(response.has_redirect_location)
        self.assertTrue(response.headers["location"], "https://auth.atlassian.com/authorize")
        self.assertIsNotNone(response.cookies.get("eave-oauth-state-atlassian"))

    async def test_atlassian_callback_endpoint(self) -> None:
        mockito.when2(eave.core.internal.oauth.atlassian.AtlassianOAuthSession.get_available_resources).thenReturn([
            eave.core.internal.oauth.atlassian.AtlassianAvailableResource(
                id=self.anystring("atlassian_cloud_id"),
                url=self.anystring("confluence_document_response._links.base"),
                avatarUrl=self.anystring("atlassianresourceavatar"),
                name=self.anystring("atlassianresourcename"),
                scopes=[],
            )
        ])

        fake_token = {
            "access_token": self.anystring("oauth_access_token"),
            "expires_in": self.anyint("oauth_expires_in"),
            "scope": self.anystring("oauth_scope"),
        }

        mockito.when2(eave.core.internal.oauth.atlassian.AtlassianOAuthSession.fetch_token, code=self.anystring("oauthcode")).thenReturn(fake_token)

        # Get the state cookie
        authorize_response = await self.make_request(
            "/oauth/atlassian/authorize",
            method="GET",
            follow_redirects=False,
        )

        self.assertEqual(authorize_response.status_code, HTTPStatus.TEMPORARY_REDIRECT)
        state = authorize_response.cookies.get("eave-oauth-state-atlassian")
        self.assertIsNotNone(state)

        async def get_installation() -> eave_orm.AtlassianInstallationOrm | None:
            installation = await eave_orm.AtlassianInstallationOrm.one_or_none_by_atlassian_cloud_id(
                session=self.dbsession,
                atlassian_cloud_id=self.anystring("atlassian_cloud_id"),
            )
            return installation

        installation = await get_installation()
        self.assertIsNone(installation)

        callback_response = await self.make_request(
            "/oauth/atlassian/callback",
            method="GET",
            payload={
                "state": state,
                "code": self.anystring("oauthcode"),
            },
        )

        self.assertEqual(callback_response.status_code, HTTPStatus.OK)

        installation = await get_installation()
        assert installation is not None
        self.assertEqual(installation.atlassian_cloud_id, self.anystring("atlassian_cloud_id"))
        self.assertEqual(installation.oauth_token_encoded, json.dumps(fake_token))
        # Test cookie was deleted
        self.assertIsNone(callback_response.cookies.get("eave-oauth-state-atlassian"))
