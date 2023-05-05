import http
import re
import urllib.parse
import uuid
from http import HTTPStatus

import eave.core.internal
import eave.core.internal.oauth.google
import eave.core.internal.oauth.slack
import eave.core.internal.orm.atlassian_installation
import eave.core.internal.orm.slack_installation
import eave.core.internal.orm.team
import eave.stdlib.core_api
import google.oauth2.credentials
import google.oauth2.id_token
import google_auth_oauthlib.flow
import google_auth_oauthlib.helpers
import mockito

from .base import BaseTestCase


class TestGoogleOAuthHandler(BaseTestCase):
    def _mock_google_auth_response(self) -> None:
        id_token = {
            "sub": self.anystring("google.sub"),
            "given_name": self.anystring("google.given_name"),
            "email": self.anystring("google.email"),
        }

        mockito.when2(google_auth_oauthlib.flow.Flow.fetch_token, **mockito.kwargs)  # do nothing

        mockito.when2(google_auth_oauthlib.helpers.credentials_from_session, ...).thenReturn(
            google.oauth2.credentials.Credentials(
                token=self.anystring("google.token"),
                refresh_token=self.anystring("google.refresh_token"),
                id_token=id_token,
            )
        )

        mockito.when2(google.oauth2.id_token.verify_oauth2_token, ...).thenReturn(id_token)

    async def test_google_authorize(self) -> None:
        response = await self.make_request(
            path="/oauth/google/authorize",
            method="GET",
            payload=None,
        )

        assert response.status_code == HTTPStatus.TEMPORARY_REDIRECT
        assert response.cookies.get("ev_oauth_state_google")
        assert response.headers["Location"]
        assert re.search(r"^https://accounts\.google\.com/o/oauth2/auth", response.headers["Location"])
        redirect_uri = urllib.parse.quote(
            f"{eave.core.internal.app_config.eave_api_base}/oauth/google/callback", safe=""
        )
        assert re.search(redirect_uri, response.headers["Location"])

    async def test_google_callback_new_account(self) -> None:
        self._mock_google_auth_response()

        assert (await self.count(eave.core.internal.orm.AccountOrm)) == 0

        response = await self.make_request(
            path="/oauth/google/callback",
            method="GET",
            payload={
                "code": self.anystring("code"),
                "state": self.anystring("state"),
            },
            cookies={
                "ev_oauth_state_google": self.anystring("state"),
            },
        )

        assert response.status_code == HTTPStatus.TEMPORARY_REDIRECT
        assert not response.cookies.get("ev_oauth_state_google")  # Test the cookie was deleted
        assert response.headers["Location"]
        assert (
            response.headers["Location"] == f"{eave.core.internal.app_config.eave_www_base}/thanks"
        )  # Default for non-whitelisted teams

        account_id = response.cookies.get("ev_account_id")
        assert account_id
        assert response.cookies.get("ev_access_token")
        assert (await self.count(eave.core.internal.orm.AccountOrm)) == 1

        eave_account = await self.get_eave_account(id=uuid.UUID(account_id))
        assert eave_account
        eave_team = await self.get_eave_team(id=eave_account.team_id)
        assert eave_team

        assert eave_account.access_token == self.anystring("google.token")
        assert eave_account.refresh_token == self.anystring("google.refresh_token")
        assert eave_account.auth_id == self.anystring("google.sub")
        assert eave_account.auth_provider == eave.stdlib.core_api.enums.AuthProvider.google
        assert eave_team.name == f"{self.anystring('google.given_name')}'s Team"

    async def test_google_callback_new_account_without_name_from_google(self) -> None:
        self.testdata["google.given_name"] = None
        self._mock_google_auth_response()

        response = await self.make_request(
            path="/oauth/google/callback",
            method="GET",
            payload={
                "code": self.anystring("code"),
                "state": self.anystring("state"),
            },
            cookies={
                "ev_oauth_state_google": self.anystring("state"),
            },
        )

        account_id = response.cookies.get("ev_account_id")
        eave_account = await self.get_eave_account(id=uuid.UUID(account_id))
        assert eave_account
        eave_team = await self.get_eave_team(id=eave_account.team_id)
        assert eave_team
        assert eave_team.name == "Your Team"

    async def test_google_callback_whitelisted_team(self) -> None:
        self._mock_google_auth_response()

        self.mock_env["EAVE_BETA_PREWHITELISTED_EMAILS_CSV"] = self.anystring("google.email")

        response = await self.make_request(
            path="/oauth/google/callback",
            method="GET",
            payload={
                "code": self.anystring("code"),
                "state": self.anystring("state"),
            },
            cookies={
                "ev_oauth_state_google": self.anystring("state"),
            },
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

    async def test_google_callback_existing_account(self) -> None:
        self._mock_google_auth_response()

        eave_team = await self.make_team()
        eave_account = await self.make_account(
            team_id=eave_team.id,
            auth_provider=eave.stdlib.core_api.enums.AuthProvider.google,
            auth_id=self.anystring("google.sub"),
            access_token=self.anystring("old_access_token"),
            refresh_token=self.anystring("old_refresh_token"),
        )

        response = await self.make_request(
            path="/oauth/google/callback",
            method="GET",
            payload={
                "code": self.anystring("code"),
                "state": self.anystring("state"),
            },
            cookies={
                "ev_oauth_state_google": self.anystring("state"),
            },
        )

        assert (await self.count(eave.core.internal.orm.AccountOrm)) == 1
        eave_account = await self.reload(eave_account)
        assert eave_account
        # Test that the tokens were updated
        assert eave_account.access_token == self.anystring("google.token")
        assert eave_account.refresh_token == self.anystring("google.refresh_token")

        # Test that the cookies were updated
        assert response.cookies.get("ev_account_id") == str(eave_account.id)
        assert response.cookies.get("ev_access_token") == eave_account.access_token

    async def test_google_callback_logged_in_account(self) -> None:
        self._mock_google_auth_response()

        eave_team = await self.make_team()
        eave_account = await self.make_account(
            team_id=eave_team.id,
            auth_provider=eave.stdlib.core_api.enums.AuthProvider.google,
            auth_id=self.anystring("google.sub"),
            access_token=self.anystring("old_access_token"),
            refresh_token=self.anystring("old_refresh_token"),
        )

        response = await self.make_request(
            path="/oauth/google/callback",
            method="GET",
            payload={
                "code": self.anystring("code"),
                "state": self.anystring("state"),
            },
            cookies={
                "ev_oauth_state_google": self.anystring("state"),
                "ev_account_id": str(eave_account.id),
                "ev_access_token": eave_account.access_token,
            },
        )

        assert (await self.count(eave.core.internal.orm.AccountOrm)) == 1
        eave_account = await self.reload(eave_account)
        assert eave_account
        # Test that the tokens were updated
        assert eave_account.access_token == self.anystring("google.token")
        assert eave_account.refresh_token == self.anystring("google.refresh_token")

        # Test that the cookies were updated
        assert response.cookies.get("ev_account_id") == str(eave_account.id)
        assert response.cookies.get("ev_access_token") == eave_account.access_token

    async def test_google_callback_logged_in_account_another_provider(self) -> None:
        self._mock_google_auth_response()

        eave_team = await self.make_team()
        eave_account_before = await self.make_account(
            team_id=eave_team.id,
            auth_provider=eave.stdlib.core_api.enums.AuthProvider.slack,
            auth_id=self.anystring("slack.user_id"),
            access_token=self.anystring("old_access_token"),
            refresh_token=self.anystring("old_refresh_token"),
        )

        response = await self.make_request(
            path="/oauth/google/callback",
            method="GET",
            payload={
                "code": self.anystring("code"),
                "state": self.anystring("state"),
            },
            cookies={
                "ev_oauth_state_google": self.anystring("state"),
                "ev_account_id": str(eave_account_before.id),
                "ev_access_token": eave_account_before.access_token,
            },
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

    async def test_google_callback_invalid_state(self) -> None:
        response = await self.make_request(
            path="/oauth/google/callback",
            method="GET",
            payload={
                "code": self.anystring("code"),
                "state": self.anystring("state"),
            },
            cookies={
                "ev_oauth_state_google": self.anystring("invalid_state"),
            },
        )

        assert response.status_code == http.HTTPStatus.BAD_REQUEST
        assert (await self.count(eave.core.internal.orm.AccountOrm)) == 0
        assert (await self.count(eave.core.internal.orm.TeamOrm)) == 0
