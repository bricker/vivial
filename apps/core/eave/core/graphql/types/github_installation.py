from typing import Optional
import uuid

import strawberry.federation as sb
from eave.core.graphql.types.mutation_result import MutationResult
from eave.core.internal.orm.github_installation import GithubInstallationOrm
from eave.stdlib.core_api.models import BaseInputModel, BaseResponseModel
import eave.core.internal.database as eave_db

@sb.type
class GithubInstallation:
    id: uuid.UUID = sb.field()
    team_id: Optional[uuid.UUID] = sb.field()
    github_install_id: str = sb.field()

    @classmethod
    def from_orm(cls, orm: GithubInstallationOrm) -> "GithubInstallation":
        return GithubInstallation(
            id=orm.id,
            team_id=orm.team_id,
            github_install_id=orm.github_install_id,
        )

@sb.input
class GithubInstallationQueryInput:
    github_install_id: str = sb.field()

class GithubInstallationResolvers:
    @staticmethod
    async def get_github_installation_for_team(team_id: uuid.UUID) -> Optional[GithubInstallation]:
        async with eave_db.async_session.begin() as db_session:
            installation = await GithubInstallationOrm.query(
                session=db_session,
                params=GithubInstallationOrm.QueryParams(
                    team_id=team_id,
                ),
            )

            if not installation:
                return None

        return GithubInstallation.from_orm(installation)

    @staticmethod
    async def get_github_installation_for_install_id(github_install_id: str) -> Optional[GithubInstallation]:
        async with eave_db.async_session.begin() as db_session:
            installation = await GithubInstallationOrm.query(
                session=db_session,
                params=GithubInstallationOrm.QueryParams(
                    github_install_id=github_install_id,
                ),
            )

            if not installation:
                return None

        return GithubInstallation.from_orm(installation)

    @staticmethod
    async def delete_github_installation(team_id: uuid.UUID, github_install_id: str) -> MutationResult:
        async with eave_db.async_session.begin() as db_session:
            await GithubInstallationOrm.delete_by_github_install_id(
                session=db_session,
                team_id=team_id,
                github_install_id=github_install_id,
            )

            return MutationResult(eave_request_id=ctx.eave_request_id)
