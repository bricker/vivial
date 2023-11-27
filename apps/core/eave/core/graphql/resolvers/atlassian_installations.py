from typing import TYPE_CHECKING, Optional
from eave.core.graphql.types.atlassian import AtlassianInstallation
from eave.core.internal import database
from eave.core.internal.orm.atlassian_installation import AtlassianInstallationOrm

if TYPE_CHECKING:
    from eave.core.graphql.types.team import Team

async def query_atlassian_installation(*, atlassian_cloud_id: str) -> Optional[AtlassianInstallation]:
    async with database.async_session.begin() as db_session:
        installation_orm = (await AtlassianInstallationOrm.query(
            session=db_session,
            params=AtlassianInstallationOrm.QueryParams(
                atlassian_cloud_id=atlassian_cloud_id,
            )
        )).one_or_none()

        return AtlassianInstallation.from_orm(installation_orm) if installation_orm else None

async def get_atlassian_installation_for_team(*, root: Team) -> Optional[AtlassianInstallation]:
    async with database.async_session.begin() as db_session:
        installation_orm = (await AtlassianInstallationOrm.query(
            session=db_session,
            params=AtlassianInstallationOrm.QueryParams(
                team_id=root.id,
            )
        )).one_or_none()

        return AtlassianInstallation.from_orm(installation_orm) if installation_orm else None
