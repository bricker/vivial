import datetime
import hashlib
from base64 import b64encode
import os
import secrets

from eave.core.internal.orm.metabase_instance import MetabaseInstanceOrm, MetabaseInstanceState

from .base import BaseTestCase


class TestMetabaseInstanceOrm(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        async with self.db_session.begin() as s:
            self._team = await self.make_team(s)

    async def test_create(self) -> None:
        async with self.db_session.begin() as s:
            metabase_instance = await MetabaseInstanceOrm.create(
                session=s,
                team_id=self._team.id,
                state=MetabaseInstanceState.READY,
            )

        assert metabase_instance.jwt_signing_key is not None
        assert metabase_instance.instance_id is not None
        assert metabase_instance.ready

    async def test_default_state(self) -> None:
        async with self.db_session.begin() as s:
            metabase_instance = MetabaseInstanceOrm(
                team_id=self._team.id,
                jwt_signing_key=secrets.token_hex(64),
                instance_id=secrets.token_hex(4),
            )
            s.add(metabase_instance)
            await s.flush()

        assert metabase_instance.ready

    async def test_internal_base_url(self) -> None:
        async with self.db_session.begin() as s:
            metabase_instance = await MetabaseInstanceOrm.create(
                session=s,
                team_id=self._team.id,
                state=MetabaseInstanceState.READY,
            )

        self.patch_env({
            "EAVE_EMBED_BASE_URL_INTERNAL": "http://embed.eave.internal"
        })

        assert metabase_instance.internal_base_url == f"http://mb-{metabase_instance.instance_id}.embed.eave.internal"

    async def test_ready(self) -> None:
        async with self.db_session.begin() as s:
            metabase_instance = await MetabaseInstanceOrm.create(
                session=s,
                team_id=self._team.id,
                state=MetabaseInstanceState.READY,
            )

        assert metabase_instance.ready

    async def test_not_ready(self) -> None:
        async with self.db_session.begin() as s:
            metabase_instance = await MetabaseInstanceOrm.create(
                session=s,
                team_id=self._team.id,
                state=MetabaseInstanceState.INIT,
            )

        assert not metabase_instance.ready
