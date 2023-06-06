from eave.core.internal.orm.confluence_destination import ConfluenceDestinationOrm
from eave.core.internal.orm.connect_installation import ConnectInstallationOrm
from eave.stdlib.core_api.models.connect import RegisterConnectInstallationInput

from .base import BaseTestCase


class ConfluenceDestinationOrmTests(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        async with self.db_session.begin() as s:
            self._data_install = await ConnectInstallationOrm.create(
                session=s,
                input=RegisterConnectInstallationInput.parse_obj(
                    {
                        "client_key": self.anystring("client_key"),
                        "product": "confluence",
                        "base_url": self.anystring("base_url"),
                        "shared_secret": self.anystring("shared_secret"),
                    }
                ),
            )

            self._data_team = await self.make_team(s)

    async def test_upsert_existing(self) -> None:
        async with self.db_session.begin() as s:
            # Create the Existing one
            dest = await ConfluenceDestinationOrm.upsert(
                session=s,
                team_id=self._data_team.id,
                connect_installation_id=self._data_install.id,
                space_key=self.anystring("space_key"),
            )

        async with self.db_session.begin() as s:
            dest_after = await ConfluenceDestinationOrm.upsert(
                session=s,
                team_id=self._data_team.id,
                connect_installation_id=self._data_install.id,
                space_key=self.anystring("updated space_key"),
            )
            assert dest_after.id == dest.id
            assert dest_after.connect_installation_id == self._data_install.id
            assert dest_after.space_key == self.getstr("updated space_key")

    async def test_upsert_new(self) -> None:
        async with self.db_session.begin() as s:
            dest = await ConfluenceDestinationOrm.upsert(
                session=s,
                team_id=self._data_team.id,
                connect_installation_id=self._data_install.id,
                space_key=self.anystring("space_key"),
            )

            assert dest.connect_installation_id == self._data_install.id
            assert dest.space_key == self.getstr("space_key")

        async with self.db_session.begin() as s:
            dest_after = await ConfluenceDestinationOrm.one_or_none(
                session=s,
                connect_installation_id=self._data_install.id,
            )
            assert dest_after is not None
            assert dest_after.space_key == self.getstr("space_key")
