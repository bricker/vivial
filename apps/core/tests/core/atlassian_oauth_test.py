from http import HTTPStatus
import json
import typing

from .base import BaseTestCase
from http import HTTPStatus
import http
import re
import uuid
import urllib.parse
import google.oauth2.credentials
import google.oauth2.id_token

import google_auth_oauthlib.flow
import google_auth_oauthlib.helpers
import eave.core.internal.database as eave_db
import eave.core.internal.oauth.atlassian
import eave.core.internal.oauth.google
import eave.core.internal.orm.atlassian_installation
import eave.core.internal.orm.atlassian_installation
import eave.core.internal.orm.team
import eave.core.internal
import eave.stdlib.core_api.operations as eave_ops
import eave.stdlib.core_api
import mockito

from .base import BaseTestCase
import eave.core.internal.oauth.atlassian

class TestAtlassianOAuth(BaseTestCase):
    def _mock_atlassian_oauth_response(self) -> None:
        self.fake_resources = [
            eave.stdlib.atlassian.AtlassianAvailableResource(
                id=self.anystring("atlassian_cloud_id"),
                url=self.anystring("confluence_document_response._links.base"),
                avatarUrl=self.anystring("atlassian.resource.avatar"),
                name=self.anystring("atlassian.resource.name"),
                scopes=[],
            )
        ]

        mockito.when2(eave.core.internal.oauth.atlassian.AtlassianOAuthSession.get_available_resources, ...).thenAnswer(
            lambda *args, **kwargs: self.fake_resources
        )

        self.fake_token = {
            "access_token": self.anystring("atlassian.access_token"),
            "refresh_token": self.anystring("atlassian.refresh_token"),
            "expires_in": self.anyint("atlassian.expires_in"),
            "scope": self.anystring("atlassian.scope"),
        }

        # Do nothing
        mockito.when2(eave.core.internal.oauth.atlassian.AtlassianOAuthSession.fetch_token, ...)
        mockito.when2(eave.core.internal.oauth.atlassian.AtlassianOAuthSession.get_token, ...).thenAnswer(lambda *args, **kwargs: self.fake_token)

        self.fake_confluence_user = eave.stdlib.atlassian.ConfluenceUser(
            data={
                "type": "known",
                "accountType": "atlassian",
                "accountId": self.anystring("confluence.account_id"),
                "displayName": self.anystring("confluence.display_name"),
                "email": self.anystring("confluence.email"),
            },
            ctx=eave.stdlib.atlassian.ConfluenceContext(base_url=self.anystring("confluence.base_url"))
        )

        mockito.when2(
            eave.core.internal.oauth.atlassian.AtlassianOAuthSession.get_userinfo, ...).thenAnswer(lambda *args, **kwargs: self.fake_confluence_user)

    async def test_atlassian_authorize_endpoint(self) -> None:
        response = await self.make_request(
            "/oauth/atlassian/authorize",
            method="GET",
            payload=None
        )

        assert response.status_code == HTTPStatus.TEMPORARY_REDIRECT
        assert response.cookies.get("ev_oauth_state_atlassian")
        assert response.headers["Location"]
        assert re.search(r"https://auth\.atlassian\.com/authorize", response.headers["Location"])
        redirect_uri = urllib.parse.quote(f"{eave.core.internal.app_config.eave_api_base}/oauth/atlassian/callback", safe="")
        assert re.search(f"redirect_uri={redirect_uri}", response.headers["Location"])

    async def test_atlassian_callback_new_account(self) -> None:
        self._mock_atlassian_oauth_response()

        assert (await self.count(eave.core.internal.orm.AccountOrm)) == 0
        assert (await self.count(eave.core.internal.orm.AtlassianInstallationOrm)) == 0

        response = await self.make_request(
            path="/oauth/atlassian/callback",
            method="GET",
            payload={
                "code": self.anystring("code"),
                "state": self.anystring("state"),
            },
            cookies={
                "ev_oauth_state_atlassian": self.anystring("state"),
            }
        )

        assert response.status_code == HTTPStatus.TEMPORARY_REDIRECT
        assert not response.cookies.get("ev_oauth_state_atlassian") # Test the cookie was deleted
        assert response.headers["Location"]
        assert response.headers["Location"] == f"{eave.core.internal.app_config.eave_www_base}/thanks" # Default for non-whitelisted teams

        account_id = response.cookies.get("ev_account_id")
        assert account_id
        assert response.cookies.get("ev_access_token") == self.anystring("atlassian.access_token")

        assert (await self.count(eave.core.internal.orm.AccountOrm)) == 1
        assert (await self.count(eave.core.internal.orm.AtlassianInstallationOrm)) == 1

        eave_account = await self.get_eave_account(id=uuid.UUID(account_id))
        assert eave_account
        eave_team = await self.get_eave_team(id=eave_account.team_id)
        assert eave_team

        async with self.db_session.begin() as db_session:
            atlassian_installation = await eave.core.internal.orm.AtlassianInstallationOrm.one_or_none(
                session=db_session,
                atlassian_cloud_id=self.anystring("atlassian_cloud_id")
            )
            assert atlassian_installation

        assert eave_account.access_token == self.anystring("atlassian.access_token")
        assert eave_account.refresh_token == self.anystring("atlassian.refresh_token")
        assert eave_account.auth_id == self.anystring("confluence.account_id")
        assert eave_account.auth_provider == eave.stdlib.core_api.enums.AuthProvider.atlassian
        assert eave_team.name == self.anystring("atlassian.resource.name")
        assert atlassian_installation.oauth_token_encoded == json.dumps(self.fake_token)
        assert atlassian_installation.atlassian_cloud_id == self.anystring("atlassian_cloud_id")
        assert atlassian_installation.team_id == eave_team.id

    async def test_atlassian_callback_new_account_without_team_name_from_atlassian(self) -> None:
        self._mock_atlassian_oauth_response()
        self.fake_resources[0].name = ""

        response = await self.make_request(
            path="/oauth/atlassian/callback",
            method="GET",
            payload={
                "code": self.anystring("code"),
                "state": self.anystring("state"),
            },
            cookies={
                "ev_oauth_state_atlassian": self.anystring("state"),
            }
        )

        account_id = response.cookies.get("ev_account_id")
        eave_account = await self.get_eave_account(id=uuid.UUID(account_id))
        assert eave_account
        eave_team = await self.get_eave_team(id=eave_account.team_id)
        assert eave_team
        assert eave_team.name == f"{self.anystring('confluence.display_name')}'s Team"

    async def test_atlassian_callback_new_account_without_user_name_from_atlassian(self) -> None:
        self._mock_atlassian_oauth_response()
        self.fake_resources[0].name = ""
        self.fake_confluence_user.display_name = None

        response = await self.make_request(
            path="/oauth/atlassian/callback",
            method="GET",
            payload={
                "code": self.anystring("code"),
                "state": self.anystring("state"),
            },
            cookies={
                "ev_oauth_state_atlassian": self.anystring("state"),
            }
        )

        account_id = response.cookies.get("ev_account_id")
        eave_account = await self.get_eave_account(id=uuid.UUID(account_id))
        assert eave_account
        eave_team = await self.get_eave_team(id=eave_account.team_id)
        assert eave_team
        assert eave_team.name == "Your Team"

    async def test_atlassian_callback_whitelisted_team(self) -> None:
        self._mock_atlassian_oauth_response()

        self.mock_env["EAVE_BETA_PREWHITELISTED_EMAILS_CSV"] = self.anystring("confluence.email")

        response = await self.make_request(
            path="/oauth/atlassian/callback",
            method="GET",
            payload={
                "code": self.anystring("code"),
                "state": self.anystring("state"),
            },
            cookies={
                "ev_oauth_state_atlassian": self.anystring("state"),
            }
        )

        account_id = response.cookies.get("ev_account_id")
        assert account_id
        eave_account = await self.get_eave_account(id=uuid.UUID(account_id))
        assert eave_account
        eave_team = await self.get_eave_team(id=eave_account.team_id)
        assert eave_team

        assert eave_team.beta_whitelisted is True
        assert response.status_code == HTTPStatus.TEMPORARY_REDIRECT
        assert response.headers["Location"]
        assert response.headers["Location"] == f"{eave.core.internal.app_config.eave_www_base}/dashboard"


    async def test_atlassian_callback_existing_account(self) -> None:
        self._mock_atlassian_oauth_response()

        eave_team = await self.make_team()
        eave_account = await self.make_account(
            team_id=eave_team.id,
            auth_provider=eave.stdlib.core_api.enums.AuthProvider.atlassian,
            auth_id=self.anystring("confluence.account_id"),
            access_token=self.anystring("old_access_token"),
            refresh_token=self.anystring("old_refresh_token"),
        )

        response = await self.make_request(
            path="/oauth/atlassian/callback",
            method="GET",
            payload={
                "code": self.anystring("code"),
                "state": self.anystring("state"),
            },
            cookies={
                "ev_oauth_state_atlassian": self.anystring("state"),
            }
        )

        assert (await self.count(eave.core.internal.orm.AccountOrm)) == 1
        eave_account = await self.reload(eave_account)
        assert eave_account
        # Test that the tokens were updated
        assert eave_account.access_token == self.anystring("atlassian.access_token")
        assert eave_account.refresh_token == self.anystring("atlassian.refresh_token")

        # Test that the cookies were updated
        assert response.cookies.get("ev_account_id") == str(eave_account.id)
        assert response.cookies.get("ev_access_token") == eave_account.access_token


    async def test_atlassian_callback_logged_in_account(self) -> None:
        self._mock_atlassian_oauth_response()

        eave_team = await self.make_team()
        eave_account = await self.make_account(
            team_id=eave_team.id,
            auth_provider=eave.stdlib.core_api.enums.AuthProvider.atlassian,
            auth_id=self.anystring("authed_user.id"),
            access_token=self.anystring("old_access_token"),
            refresh_token=self.anystring("old_refresh_token"),
        )

        response = await self.make_request(
            path="/oauth/atlassian/callback",
            method="GET",
            payload={
                "code": self.anystring("code"),
                "state": self.anystring("state"),
            },
            cookies={
                "ev_oauth_state_atlassian": self.anystring("state"),
                "ev_account_id": str(eave_account.id),
                "ev_access_token": eave_account.access_token,
            }
        )

        assert (await self.count(eave.core.internal.orm.AccountOrm)) == 1
        eave_account = await self.reload(eave_account)
        assert eave_account
        # Test that the tokens were updated
        assert eave_account.access_token == self.anystring("atlassian.access_token")
        assert eave_account.refresh_token == self.anystring("atlassian.refresh_token")

        # Test that the cookies were updated
        assert response.cookies.get("ev_account_id") == str(eave_account.id)
        assert response.cookies.get("ev_access_token") == eave_account.access_token

    async def test_atlassian_callback_logged_in_account_another_provider(self) -> None:
        self._mock_atlassian_oauth_response()

        eave_team = await self.make_team()
        eave_account_before = await self.make_account(
            team_id=eave_team.id,
            auth_provider=eave.stdlib.core_api.enums.AuthProvider.slack,
            auth_id=self.anystring("slack.user_id"),
            access_token=self.anystring("old_access_token"),
            refresh_token=self.anystring("old_refresh_token"),
        )

        response = await self.make_request(
            path="/oauth/atlassian/callback",
            method="GET",
            payload={
                "code": self.anystring("code"),
                "state": self.anystring("state"),
            },
            cookies={
                "ev_oauth_state_atlassian": self.anystring("state"),
                "ev_account_id": str(eave_account_before.id),
                "ev_access_token": eave_account_before.access_token,
            }
        )

        assert (await self.count(eave.core.internal.orm.AccountOrm)) == 1
        eave_account_after = await self.reload(eave_account_before)
        assert eave_account_after
        # Test that the tokens were NOT updated
        assert eave_account_after.access_token == self.anystring("old_access_token")
        assert eave_account_after.refresh_token == self.anystring("old_refresh_token")

        # Test that the cookies were NOT updated
        assert response.cookies.get("ev_account_id") == str(eave_account_before.id)
        assert response.cookies.get("ev_access_token") == eave_account_before.access_token

    async def test_atlassian_callback_invalid_state(self) -> None:
        response = await self.make_request(
            path="/oauth/atlassian/callback",
            method="GET",
            payload={
                "code": self.anystring("code"),
                "state": self.anystring("state"),
            },
            cookies={
                "ev_oauth_state_atlassian": self.anystring("invalid_state"),
            }
        )

        assert response.status_code == http.HTTPStatus.BAD_REQUEST
        assert (await self.count(eave.core.internal.orm.AccountOrm)) == 0
        assert (await self.count(eave.core.internal.orm.TeamOrm)) == 0

    async def test_atlassian_default_confluence_space(self) -> None:
        self.skipTest("TODO")