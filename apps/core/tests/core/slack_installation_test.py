import unittest.mock
import eave.core.internal
from eave.core.internal.orm.resource_mutex import ResourceMutexOrm
from eave.core.internal.orm.slack_installation import SlackInstallationOrm
from .base import BaseTestCase

mut = eave.core.internal.orm.slack_installation.__name__


class TestSlackInstallation(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.patch(
            name="slack.refresh_access_token_or_exception",
            patch=unittest.mock.patch(
                "eave.core.internal.oauth.slack.refresh_access_token_or_exception",
                return_value={
                    "access_token": self.anystring("access_token"),
                    "refresh_token": self.anystring("refresh_token"),
                    "expires_in": (60 * 60 * 12),
                    "team": {"id": self.anystring("team.id"), "name": self.anystring("team.name")},
                    "authed_user": {
                        "id": self.anystring("authed_user.id"),
                        "access_token": self.anystring("authed_user.access_token"),
                        "refresh_token": self.anystring("authed_user.refresh_token"),
                        "expires_in": (60 * 60 * 12),
                    },
                },
            ),
        )

        self.patch(
            name="ResourceMutexOrm", patch=unittest.mock.patch(f"{mut}.ResourceMutexOrm", wraps=ResourceMutexOrm)
        )
        async with self.db_session.begin() as s:
            self.data_team = await self.make_team(s)

    async def test_refresh_token_with_far_expiry_does_not_refresh(self) -> None:
        async with self.db_session.begin() as s:
            expiry = self.anydatetime("bot_token_exp", offset=60 * 120)
            installation_before = await SlackInstallationOrm.create(
                session=s,
                team_id=self.data_team.id,
                slack_team_id=self.anystring("slack_team_id"),
                bot_token=self.anystring("bot_token"),
                bot_refresh_token=self.anystring("bot_refresh_token"),
                bot_token_exp=expiry,
            )

            installation_after = await self.reload(s, installation_before)
            assert installation_after

            await installation_after.refresh_token_or_exception(session=s)

            assert self.get_mock("slack.refresh_access_token_or_exception").call_count == 0
            assert self.get_mock("ResourceMutexOrm").acquire.call_count == 0
            assert installation_after.bot_token == self.anystring("bot_token")
            assert installation_after.bot_refresh_token == self.anystring("bot_refresh_token")
            assert installation_after.bot_token_exp
            assert installation_after.bot_token_exp == expiry

    async def test_refresh_token_with_close_expiry_refreshes_token(self) -> None:
        async with self.db_session.begin() as s:
            expiry = self.anydatetime("bot_token_exp", offset=10)
            installation_before = await SlackInstallationOrm.create(
                session=s,
                team_id=self.data_team.id,
                slack_team_id=self.anystring("slack_team_id"),
                bot_token=self.anystring("bot_token"),
                bot_refresh_token=self.anystring("bot_refresh_token"),
                bot_token_exp=expiry,
            )

            installation_after = await self.reload(s, installation_before)
            assert installation_after

            assert self.get_mock("slack.refresh_access_token_or_exception").call_count == 0
            assert self.get_mock("ResourceMutexOrm").acquire.call_count == 0
            assert self.get_mock("ResourceMutexOrm").release.call_count == 0

            await installation_after.refresh_token_or_exception(session=s)

            assert self.get_mock("slack.refresh_access_token_or_exception").call_count == 1
            assert self.get_mock("ResourceMutexOrm").acquire.call_count == 1
            assert self.get_mock("ResourceMutexOrm").release.call_count == 1
            assert installation_after.bot_token != self.anystring("bot_token")
            assert installation_after.bot_refresh_token != self.anystring("bot_refresh_token")
            assert installation_after.bot_token_exp
            assert installation_after.bot_token_exp > expiry

    async def test_refresh_token_without_acquire_doesnt_refresh_token(self) -> None:
        async with self.db_session.begin() as s:
            expiry = self.anydatetime("bot_token_exp", offset=10)
            installation_before = await SlackInstallationOrm.create(
                session=s,
                team_id=self.data_team.id,
                slack_team_id=self.anystring("slack_team_id"),
                bot_token=self.anystring("bot_token"),
                bot_refresh_token=self.anystring("bot_refresh_token"),
                bot_token_exp=expiry,
            )

            acquired = await ResourceMutexOrm.acquire(session=s, resource_id=installation_before.id)
            assert acquired

            installation_after = await self.reload(s, installation_before)
            assert installation_after

            assert self.get_mock("ResourceMutexOrm").acquire.call_count == 0

            await installation_after.refresh_token_or_exception(session=s)

            assert self.get_mock("ResourceMutexOrm").acquire.call_count == 1
            assert self.get_mock("ResourceMutexOrm").release.call_count == 0

            # WARNING: This assertion will fail if you're on a breakpoint for more than 60 seconds, because `acquire` automatically
            # releases stuck locks.
            assert self.get_mock("slack.refresh_access_token_or_exception").call_count == 0
            assert installation_after.bot_token == self.anystring("bot_token")
            assert installation_after.bot_refresh_token == self.anystring("bot_refresh_token")
            assert installation_after.bot_token_exp
            assert installation_after.bot_token_exp == expiry

            await ResourceMutexOrm.release(session=s, resource_id=installation_before.id)

    async def test_lock_is_released_on_error(self) -> None:
        async with self.db_session.begin() as s:
            expiry = self.anydatetime("bot_token_exp", offset=10)
            installation_before = await SlackInstallationOrm.create(
                session=s,
                team_id=self.data_team.id,
                slack_team_id=self.anystring("slack_team_id"),
                bot_token=self.anystring("bot_token"),
                bot_refresh_token=self.anystring("bot_refresh_token"),
                bot_token_exp=expiry,
            )

            installation_after = await self.reload(s, installation_before)
            assert installation_after

            self.get_mock("slack.refresh_access_token_or_exception").side_effect = Exception("fake error for testing")
            await installation_after.refresh_token_or_exception(session=s)

            assert (await self.count(s, ResourceMutexOrm)) == 0
            assert self.get_mock("ResourceMutexOrm").release.call_count == 1
