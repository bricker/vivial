import http

from sqlalchemy.exc import SQLAlchemyError
from eave.core.internal.orm.forge_installation import ForgeInstallationOrm
from eave.core.internal.orm.team import TeamOrm
from eave.stdlib.core_api.operations.forge import QueryForgeInstallation, RegisterForgeInstallation, RegisterForgeInstallationInput, UpdateForgeInstallation
from .base import BaseTestCase


class ForgeEndpointsTest(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    async def test_register_forge_installation(self) -> None:
        response = await self.make_request(
            path="/integrations/forge/register",
            payload={
                "forge_integration": {
                    "forge_app_id": self.anystring("forge_app_id"),
                    "forge_app_version": self.anystring("forge_app_version"),
                    "forge_app_installation_id": self.anystring("forge_app_installation_id"),
                    "forge_app_installer_account_id": self.anystring("forge_app_installer_account_id"),
                    "webtrigger_url": self.anystring("webtrigger_url"),
                    "confluence_space_key": self.anystring("confluence_space_key"),
                },
            },
        )

        assert response.status_code == http.HTTPStatus.OK
        obj = RegisterForgeInstallation.ResponseBody(**response.json())
        assert obj.forge_integration.forge_app_installation_id == self.getstr("forge_app_installation_id")

        assert self.logged_event(
            event_name="eave_application_integration",
            eave_account_id="unknown",
            eave_visitor_id="unknown",
            eave_team_id="unknown",
            opaque_params={
                "integration_name": "forge",
            }
        )

        async with self.db_session.begin() as s:
            install = await ForgeInstallationOrm.one_or_none(
                session=s,
                forge_app_installation_id=self.getstr("forge_app_installation_id"),
            )
            assert install is not None
            assert install.forge_app_id == self.getstr("forge_app_id")
            assert install.forge_app_version == self.getstr("forge_app_version")
            assert install.forge_app_installation_id == self.getstr("forge_app_installation_id")
            assert install.forge_app_installer_account_id == self.getstr("forge_app_installer_account_id")
            assert install.webtrigger_url == self.getstr("webtrigger_url")
            assert install.confluence_space_key == self.getstr("confluence_space_key")


    async def test_register_forge_installation_with_no_confluence_space(self) -> None:
        response = await self.make_request(
            path="/integrations/forge/register",
            payload={
                "forge_integration": {
                    "forge_app_id": self.anystring("forge_app_id"),
                    "forge_app_version": self.anystring("forge_app_version"),
                    "forge_app_installation_id": self.anystring("forge_app_installation_id"),
                    "forge_app_installer_account_id": self.anystring("forge_app_installer_account_id"),
                    "webtrigger_url": self.anystring("webtrigger_url"),
                    "confluence_space_key": None,
                },
            },
        )

        assert response.status_code == http.HTTPStatus.OK
        obj = RegisterForgeInstallation.ResponseBody(**response.json())
        assert obj.forge_integration.confluence_space_key is None

        async with self.db_session.begin() as s:
            install = await ForgeInstallationOrm.one_or_none(
                session=s,
                forge_app_installation_id=self.getstr("forge_app_installation_id"),
            )
            assert install is not None
            assert install.confluence_space_key is None


    async def test_update_forge_installation_with_no_team(self) -> None:
        async with self.db_session.begin() as s:
            await ForgeInstallationOrm.create(
                session=s,
                input=RegisterForgeInstallationInput(
                    forge_app_id=self.anystring("forge_app_id"),
                    forge_app_version=self.anystring("forge_app_version"),
                    forge_app_installation_id=self.anystring("forge_app_installation_id"),
                    forge_app_installer_account_id=self.anystring("forge_app_installer_account_id"),
                    webtrigger_url=self.anystring("webtrigger_url"),
                    confluence_space_key=None,
                )
            )

        response = await self.make_request(
            path="/integrations/forge/update",
            payload={
                "forge_integration": {
                    "forge_app_installation_id": self.anystring("forge_app_installation_id"),
                    "forge_app_version": self.anystring("forge_app_version_2"),
                    "confluence_space_key": self.anystring("confluence_space_key"),
                },
            },
        )

        assert response.status_code == http.HTTPStatus.OK
        obj = UpdateForgeInstallation.ResponseBody(**response.json())
        assert obj.forge_integration.forge_app_installation_id == self.getstr("forge_app_installation_id")
        assert obj.forge_integration.forge_app_version == self.getstr("forge_app_version_2")
        assert obj.forge_integration.confluence_space_key == self.getstr("confluence_space_key")

        assert self.logged_event(
            event_name="eave_forge_app_updated",
            eave_team_id=None,
            opaque_params={
                "integration_name": "forge",
                "forge_app_previous_version": self.getstr("forge_app_version"),
                "forge_app_new_version": self.getstr("forge_app_version_2")
            }
        )

        async with self.db_session.begin() as s:
            install_after = await ForgeInstallationOrm.one_or_none(
                session=s,
                forge_app_installation_id=self.getstr("forge_app_installation_id"),
            )
            assert install_after is not None
            assert install_after.forge_app_version == self.getstr("forge_app_version_2")
            assert install_after.forge_app_installation_id == self.getstr("forge_app_installation_id")
            assert install_after.forge_app_installer_account_id == self.getstr("forge_app_installer_account_id")
            assert install_after.webtrigger_url == self.getstr("webtrigger_url")
            assert install_after.confluence_space_key == self.getstr("confluence_space_key")

    async def test_update_forge_installation_with_team(self) -> None:
        async with self.db_session.begin() as s:
            eave_team = await TeamOrm.create(
                session=s,
                name=self.anystring(),
            )

            await ForgeInstallationOrm.create(
                session=s,
                team_id=eave_team.id,
                input=RegisterForgeInstallationInput(
                    forge_app_id=self.anystring("forge_app_id"),
                    forge_app_version=self.anystring("forge_app_version"),
                    forge_app_installation_id=self.anystring("forge_app_installation_id"),
                    forge_app_installer_account_id=self.anystring("forge_app_installer_account_id"),
                    webtrigger_url=self.anystring("webtrigger_url"),
                    confluence_space_key=None,
                )
            )

        response = await self.make_request(
            path="/integrations/forge/update",
            payload={
                "forge_integration": {
                    "forge_app_installation_id": self.anystring("forge_app_installation_id"),
                    "forge_app_version": self.anystring("forge_app_version_2"),
                    "confluence_space_key": self.anystring("confluence_space_key"),
                },
            },
        )

        assert response.status_code == http.HTTPStatus.OK
        obj = UpdateForgeInstallation.ResponseBody(**response.json())
        assert obj.forge_integration.forge_app_installation_id == self.getstr("forge_app_installation_id")
        assert obj.team is not None
        assert obj.team.id == eave_team.id

        assert self.logged_event(
            event_name="eave_forge_app_updated",
            eave_team_id=str(eave_team.id),
        )

        async with self.db_session.begin() as s:
            install_after = await ForgeInstallationOrm.one_or_none(
                session=s,
                forge_app_installation_id=self.getstr("forge_app_installation_id"),
                team_id=eave_team.id,
            )
            assert install_after is not None

    async def test_query_forge_installation_with_team(self) -> None:
        async with self.db_session.begin() as s:
            eave_team = await TeamOrm.create(
                session=s,
                name=self.anystring(),
            )

            await ForgeInstallationOrm.create(
                session=s,
                team_id=eave_team.id,
                input=RegisterForgeInstallationInput(
                    forge_app_id=self.anystring("forge_app_id"),
                    forge_app_version=self.anystring("forge_app_version"),
                    forge_app_installation_id=self.anystring("forge_app_installation_id"),
                    forge_app_installer_account_id=self.anystring("forge_app_installer_account_id"),
                    webtrigger_url=self.anystring("webtrigger_url"),
                    confluence_space_key=None,
                )
            )

        response = await self.make_request(
            path="/integrations/forge/query",
            payload={
                "forge_integration": {
                    "forge_app_id": self.anystring("forge_app_id"),
                    "forge_app_installation_id": self.anystring("forge_app_installation_id"),
                },
            },
        )

        assert response.status_code == http.HTTPStatus.OK
        obj = QueryForgeInstallation.ResponseBody(**response.json())
        assert obj.forge_integration.forge_app_installation_id == self.getstr("forge_app_installation_id")
        assert obj.team is not None
        assert obj.team.id == eave_team.id

    async def test_query_forge_installation_with_no_team(self) -> None:
        async with self.db_session.begin() as s:
            await ForgeInstallationOrm.create(
                session=s,
                input=RegisterForgeInstallationInput(
                    forge_app_id=self.anystring("forge_app_id"),
                    forge_app_version=self.anystring("forge_app_version"),
                    forge_app_installation_id=self.anystring("forge_app_installation_id"),
                    forge_app_installer_account_id=self.anystring("forge_app_installer_account_id"),
                    webtrigger_url=self.anystring("webtrigger_url"),
                    confluence_space_key=None,
                )
            )

        response = await self.make_request(
            path="/integrations/forge/query",
            payload={
                "forge_integration": {
                    "forge_app_id": self.anystring("forge_app_id"),
                    "forge_app_installation_id": self.anystring("forge_app_installation_id"),
                },
            },
        )

        assert response.status_code == http.HTTPStatus.OK
        obj = QueryForgeInstallation.ResponseBody(**response.json())
        assert obj.forge_integration.forge_app_installation_id == self.getstr("forge_app_installation_id")
        assert obj.team is None

    async def test_query_forge_installation_not_found(self) -> None:
        with self.assertRaises(SQLAlchemyError):
            await self.make_request(
                path="/integrations/forge/query",
                payload={
                    "forge_integration": {
                        "forge_app_id": self.anystring("forge_app_id"),
                        "forge_app_installation_id": self.anystring("forge_app_installation_id"),
                    },
                },
            )
