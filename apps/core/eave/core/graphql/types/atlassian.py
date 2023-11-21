import uuid
from typing import List, Optional

import strawberry.federation as sb
from eave.core.internal.orm.atlassian_installation import AtlassianInstallationOrm
from eave.core.internal.orm.team import TeamOrm
from eave.stdlib.core_api.models import BaseInputModel, BaseResponseModel
import eave.core.internal.database as eave_db


@sb.type
class ConfluenceSpace:
    key: str = sb.field()
    name: str = sb.field()

@sb.type
class AtlassianInstallation:
    id: uuid.UUID = sb.field()
    team_id: uuid.UUID = sb.field()
    atlassian_cloud_id: str = sb.field()

    @classmethod
    def from_orm(cls, orm: AtlassianInstallationOrm) -> "AtlassianInstallation":
        return AtlassianInstallation(
            id=orm.id,
            team_id=orm.team_id,
            atlassian_cloud_id=orm.atlassian_cloud_id
        )

@sb.input
class AtlassianInstallationInput:
    atlassian_cloud_id: str = sb.field()

class AtlassianInstallationResolvers:
    @staticmethod
    async def get_atlassian_installation_for_team(team_id: uuid.UUID) -> Optional[AtlassianInstallation]:
        async with eave_db.async_session.begin() as db_session:
            installation = await AtlassianInstallationOrm.one_or_none(
                session=db_session,
                atlassian_cloud_id=input.atlassian_integration.atlassian_cloud_id,
            )

            if not installation:
                return None

            eave_team = await TeamOrm.one_or_exception(
                session=db_session,
                team_id=installation.team_id,
            )

        return eave_api_util.json_response(
            GetAtlassianInstallation.ResponseBody(
                atlassian_integration=installation.api_model,
                team=eave_team.api_model,
            )
        )

    @staticmethod
    async def get_atlassian_installation_for_cloud_id(atlassian_cloud_id: str) -> Optional[AtlassianInstallation]:
        async with eave_db.async_session.begin() as db_session:
            installation = await eave_orm.AtlassianInstallationOrm.one_or_none(
                session=db_session,
                atlassian_cloud_id=input.atlassian_integration.atlassian_cloud_id,
            )

            if not installation:
                raise NotFoundError()

            eave_team = await eave_orm.TeamOrm.one_or_exception(
                session=db_session,
                team_id=installation.team_id,
            )

        return eave_api_util.json_response(
            GetAtlassianInstallation.ResponseBody(
                atlassian_integration=installation.api_model,
                team=eave_team.api_model,
            )
        )
