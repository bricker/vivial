from typing import Optional
import sqlalchemy.exc

import eave.core.internal.database as eave_db
from eave.core.internal.orm.client_credentials import ClientCredentialsOrm, ClientScope
from eave.core.internal.orm.confluence_destination import ConfluenceDestinationOrm
from eave.core.internal.orm.connect_installation import ConnectInstallationOrm
from eave.core.internal.orm.team import TeamOrm
from eave.stdlib.core_api.models.connect import AtlassianProduct

from .base import BaseTestCase


class TestClientCredentialsOrmScopeQuery(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        async with self.db_session.begin() as s:
            self._team = await self.make_team(s)

    async def _create_creds(self, scope: ClientScope) -> ClientCredentialsOrm:
        async with self.db_session.begin() as s:
            creds = await ClientCredentialsOrm.create(
                session=s,
                team_id=self._team.id,
                description=None,
                scope=scope,
            )

        return creds

    async def _query_creds(self, creds: ClientCredentialsOrm, scope: ClientScope) -> Optional[ClientCredentialsOrm]:
        async with self.db_session.begin() as s:
            qresult = (await ClientCredentialsOrm.query(
                session=s,
                params=ClientCredentialsOrm.QueryParams(
                    id=creds.id,
                    secret=creds.secret,
                    scope_includes=scope,
                ),
            )).one_or_none()

        return qresult

    async def test_query_scope_readonly(self) -> None:
        creds = await self._create_creds(ClientScope.readonly)

        qresult = await self._query_creds(creds, ClientScope.readonly)

        assert qresult is not None
        assert qresult.scope