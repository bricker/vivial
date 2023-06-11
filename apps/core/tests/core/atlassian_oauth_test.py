import asyncio
import oauthlib.oauth2.rfc6749.tokens
import http
import json
import re
import unittest.mock
import urllib.parse
import uuid
from http import HTTPStatus
from eave.core.internal.orm.account import AccountOrm

import eave.stdlib.atlassian

import eave.core.internal
import eave.core.internal.oauth.atlassian
import eave.core.internal.oauth.google
from eave.core.internal.orm.atlassian_installation import AtlassianInstallationOrm
import eave.core.internal.orm.team
from eave.stdlib.core_api.models.account import AuthProvider
from eave.stdlib.core_api.models.team import DocumentPlatform

from .base import BaseTestCase


class TestAtlassianOAuth(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    async def test_token_update(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)

            sut = await AtlassianInstallationOrm.create(
                atlassian_cloud_id=self.anystring(),
                oauth_token_encoded=self.anyjson(),
                session=s,
                team_id=team.id,
            )

        token = oauthlib.oauth2.rfc6749.tokens.OAuth2Token(self.anydict("token"))
        sut.token_updater_factory()(token)
        await asyncio.gather(*sut._tasks)

        async with self.db_session.begin() as s:
            sut_after = await self.reload(s, sut)
            assert sut_after
            assert sut_after.oauth_token_decoded == token

    async def test_atlassian_authorize_endpoint(self) -> None:
        response = await self.make_request("/oauth/atlassian/authorize", method="GET", payload=None)

        assert response.status_code == HTTPStatus.TEMPORARY_REDIRECT
        assert response.cookies.get("ev_oauth_state_atlassian")
        assert response.headers["Location"]
        assert re.search(r"https://auth\.atlassian\.com/authorize", response.headers["Location"])
        redirect_uri = urllib.parse.quote(
            f"{eave.core.internal.app_config.eave_api_base}/oauth/atlassian/callback", safe=""
        )
        assert re.search(f"redirect_uri={redirect_uri}", response.headers["Location"])

    async def test_atlassian_callback_new_account(self) -> None:
        async with self.db_session.begin() as s:
            assert (await self.count(s, eave.core.internal.orm.AccountOrm)) == 0
            assert (await self.count(s, eave.core.internal.orm.AtlassianInstallationOrm)) == 0

        response = await self.make_request(
            path="/oauth/atlassian/callback",
            method="GET",
            payload={
                "code": self.anystring("code"),
                "state": self.anystring("state"),
            },
            cookies={
                "ev_oauth_state_atlassian": self.anystring("state"),
            },
        )

        async with self.db_session.begin() as s:
            assert response.status_code == HTTPStatus.TEMPORARY_REDIRECT
            assert not response.cookies.get("ev_oauth_state_atlassian")  # Test the cookie was deleted
            assert response.headers["Location"]
            assert (
                response.headers["Location"] == f"{eave.core.internal.app_config.eave_www_base}/dashboard"
            )

            account_id = response.cookies.get("ev_account_id")
            assert account_id
            assert response.cookies.get("ev_access_token") == self.anystring("atlassian.access_token")

            assert (await self.count(s, eave.core.internal.orm.AccountOrm)) == 1
            assert (await self.count(s, eave.core.internal.orm.AtlassianInstallationOrm)) == 1

            eave_account = await self.get_eave_account(s, id=uuid.UUID(account_id))
            assert eave_account
            eave_team = await self.get_eave_team(s, id=eave_account.team_id)
            assert eave_team

            atlassian_installation = await eave.core.internal.orm.AtlassianInstallationOrm.one_or_none(
                session=s, atlassian_cloud_id=self.anystring("atlassian_cloud_id")
            )
            assert atlassian_installation

            assert eave_account.access_token == self.getstr("atlassian.access_token")
            assert eave_account.refresh_token == self.getstr("atlassian.refresh_token")
            assert eave_account.auth_id == self.getstr("confluence.account_id")
            assert eave_account.auth_provider == AuthProvider.atlassian
            assert eave_team.name == self.getstr("atlassian.resource.name")
            assert eave_team.document_platform is None # No connect installation has been linked yet
            assert atlassian_installation.oauth_token_encoded == json.dumps(self.testdata["fake_atlassian_token"])
            assert atlassian_installation.atlassian_cloud_id == self.getstr("atlassian_cloud_id")
            assert atlassian_installation.team_id == eave_team.id
            assert atlassian_installation.atlassian_site_name == self.getstr("atlassian.resource.name")

    async def test_atlassian_callback_new_account_without_team_name_from_atlassian(self) -> None:
        self.testdata["fake_atlassian_resources"][0].name = ""
        self.testdata["fake_atlassian_resources"][0].url = self.anystring("atlassian url")

        response = await self.make_request(
            path="/oauth/atlassian/callback",
            method="GET",
            payload={
                "code": self.anystring("code"),
                "state": self.anystring("state"),
            },
            cookies={
                "ev_oauth_state_atlassian": self.anystring("state"),
            },
        )

        async with self.db_session.begin() as s:
            account_id = response.cookies.get("ev_account_id")
            eave_account = await self.get_eave_account(s, id=uuid.UUID(account_id))
            assert eave_account
            eave_team = await self.get_eave_team(s, id=eave_account.team_id)
            assert eave_team
            assert eave_team.name == f"{self.getstr('confluence.display_name')}'s Team"

            atlassian_installation = await eave.core.internal.orm.AtlassianInstallationOrm.one_or_none(
                session=s, atlassian_cloud_id=self.getstr("atlassian_cloud_id")
            )

            assert atlassian_installation
            assert atlassian_installation.atlassian_site_name == self.getstr("atlassian url")

    async def test_atlassian_callback_new_account_without_user_name_from_atlassian(self) -> None:
        self.testdata["fake_atlassian_resources"][0].name = ""
        self.testdata["fake_confluence_user"].display_name = None

        response = await self.make_request(
            path="/oauth/atlassian/callback",
            method="GET",
            payload={
                "code": self.anystring("code"),
                "state": self.anystring("state"),
            },
            cookies={
                "ev_oauth_state_atlassian": self.anystring("state"),
            },
        )

        async with self.db_session.begin() as s:
            account_id = response.cookies.get("ev_account_id")
            eave_account = await self.get_eave_account(s, id=uuid.UUID(account_id))
            assert eave_account
            eave_team = await self.get_eave_team(s, id=eave_account.team_id)
            assert eave_team
            assert eave_team.name == "Your Team"

    async def test_atlassian_callback_whitelisted_team(self) -> None:
        self.patch_dict(
            unittest.mock.patch.dict(
                "os.environ",
                {
                    "EAVE_BETA_PREWHITELISTED_EMAILS_CSV": self.anystring("confluence.email"),
                },
            ),
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
            },
        )

        async with self.db_session.begin() as s:
            account_id = response.cookies.get("ev_account_id")
            assert account_id
            eave_account = await self.get_eave_account(s, id=uuid.UUID(account_id))
            assert eave_account
            eave_team = await self.get_eave_team(s, id=eave_account.team_id)
            assert eave_team

            assert eave_team.beta_whitelisted is True
            assert response.status_code == HTTPStatus.TEMPORARY_REDIRECT
            assert response.headers["Location"]
            assert response.headers["Location"] == f"{eave.core.internal.app_config.eave_www_base}/dashboard"

    async def test_atlassian_callback_existing_account(self) -> None:
        async with self.db_session.begin() as s:
            eave_team = await self.make_team(s)
            eave_account_before = await self.make_account(
                s,
                team_id=eave_team.id,
                auth_provider=AuthProvider.atlassian,
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
            },
        )

        async with self.db_session.begin() as s:
            assert (await self.count(s, eave.core.internal.orm.AccountOrm)) == 1
            eave_account_after = await AccountOrm.one_or_exception(session=s, id=eave_account_before.id)

            # Test that the tokens were updated
            assert eave_account_after.access_token == self.anystring("atlassian.access_token")
            assert eave_account_after.refresh_token == self.anystring("atlassian.refresh_token")

            # Test that the cookies were updated
            assert response.cookies.get("ev_account_id") == str(eave_account_after.id)
            assert response.cookies.get("ev_access_token") == eave_account_after.access_token

    async def test_atlassian_callback_logged_in_account(self) -> None:
        async with self.db_session.begin() as s:
            eave_team = await self.make_team(s)
            eave_account_before = await self.make_account(
                s,
                team_id=eave_team.id,
                auth_provider=AuthProvider.atlassian,
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
                "ev_account_id": str(eave_account_before.id),
                "ev_access_token": eave_account_before.access_token,
            },
        )

        async with self.db_session.begin() as s:
            assert (await self.count(s, eave.core.internal.orm.AccountOrm)) == 1
            eave_account_after = await self.reload(s, eave_account_before)
            assert eave_account_after
            # Test that the tokens were updated
            assert eave_account_after.access_token == self.anystring("atlassian.access_token")
            assert eave_account_after.refresh_token == self.anystring("atlassian.refresh_token")

            # Test that the cookies were updated
            assert response.cookies.get("ev_account_id") == str(eave_account_after.id)
            assert response.cookies.get("ev_access_token") == eave_account_after.access_token

    async def test_atlassian_callback_logged_in_account_another_provider(self) -> None:
        async with self.db_session.begin() as s:
            eave_team = await self.make_team(s)
            eave_account_before = await self.make_account(
                s,
                team_id=eave_team.id,
                auth_provider=AuthProvider.slack,
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
            },
        )

        async with self.db_session.begin() as s:
            assert (await self.count(s, eave.core.internal.orm.AccountOrm)) == 1
            eave_account_after = await self.reload(s, eave_account_before)
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
            },
        )

        async with self.db_session.begin() as s:
            assert response.status_code == http.HTTPStatus.BAD_REQUEST
            assert (await self.count(s, eave.core.internal.orm.AccountOrm)) == 0
            assert (await self.count(s, eave.core.internal.orm.TeamOrm)) == 0

    async def test_atlassian_default_confluence_space(self) -> None:
        self.skipTest("TODO")
