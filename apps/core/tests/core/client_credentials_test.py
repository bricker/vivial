import datetime
import hashlib
from base64 import b64encode

from eave.core.internal.orm.client_credentials import ClientCredentialsOrm, ClientScope

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

    async def _query_creds(self, creds: ClientCredentialsOrm, scope: ClientScope) -> ClientCredentialsOrm | None:
        async with self.db_session.begin() as s:
            qresult = (
                await ClientCredentialsOrm.query(
                    session=s,
                    params=ClientCredentialsOrm.QueryParams(
                        id=creds.id,
                        secret=creds.secret,
                        scope_includes=scope,
                    ),
                )
            ).one_or_none()

        return qresult

    async def test_query_scope_readonly(self) -> None:
        creds = await self._create_creds(ClientScope.read)

        qresult = await self._query_creds(creds, ClientScope.read)

        assert qresult is not None
        assert qresult.scope

    async def test_touch(self) -> None:
        creds = await self._create_creds(ClientScope.read)
        assert creds.last_used is None

        async with self.db_session.begin() as s:
            creds.touch(s)

        assert creds.last_used is not None
        assert creds.last_used > datetime.datetime.now(datetime.UTC).replace(tzinfo=None) - datetime.timedelta(seconds=5)

    async def test_combined(self) -> None:
        creds = await self._create_creds(ClientScope.read)
        assert creds.combined == f"{creds.id}:{creds.secret}"

    async def test_decryption_key(self) -> None:
        creds = await self._create_creds(ClientScope.read)
        assert creds.decryption_key == b64encode(hashlib.sha256(bytes(creds.combined, "utf-8")).digest())
