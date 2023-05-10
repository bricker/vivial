import eave.core.internal.database as eave_db
from eave.core.internal import app_config
import eave.core.internal.orm as eave_orm
import eave.core.public.request_state as eave_rutil
from eave.core.public.http_endpoint import HTTPEndpoint


import eave.stdlib.api_util as eave_api_util
import eave.stdlib.core_api as eave_core
from starlette.requests import Request
from starlette.responses import Response


class QueryForgeIntegration(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        # FIXME: Proper request authorization (signing)
        shared_secret = request.headers.get("eave-secret")
        assert shared_secret and shared_secret == app_config.eave_forge_shared_secret

        eave_rutil.get_eave_state(request=request)
        body = await request.json()
        input = eave_core.operations.forge.QueryForgeInstallation.RequestBody.parse_obj(body)

        async with eave_db.async_session.begin() as db_session:
            installation = await eave_orm.ForgeInstallationOrm.one_or_exception(
                session=db_session,
                forge_app_installation_id=input.forge_integration.forge_app_installation_id,
            )

            triggers = await eave_orm.ForgeWebTriggerOrm.query(
                session=db_session,
                team_id=installation.team_id,
                forge_installation_id=installation.id,
            )

            eave_team = await eave_orm.TeamOrm.one_or_exception(
                session=db_session,
                team_id=installation.team_id,
            )

        eave_team = eave_core.models.Team.from_orm(eave_team)
        forge_integration = eave_core.models.forge.ForgeInstallation.from_orm(installation)
        forge_web_triggers = eave_orm.ForgeWebTriggerOrm.mapping(triggers)

        return eave_api_util.json_response(
            eave_core.operations.forge.QueryForgeInstallation.ResponseBody(
                team=eave_team,
                forge_integration=forge_integration,
                forge_web_triggers=forge_web_triggers,
            )
        )


class RegisterForgeIntegration(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        eave_rutil.get_eave_state(request=request)
        body = await request.json()
        input = eave_core.operations.forge.RegisterForgeInstallation.RequestBody.parse_obj(body)

        async with eave_db.async_session.begin() as db_session:
            installation_orm = await eave_orm.ForgeInstallationOrm.create(
                session=db_session,
                team_id=,
                input=input.forge_integration,
            )

            triggers: list[eave_orm.ForgeWebTriggerOrm] = []

            if input.forge_web_triggers:
                for trigger in input.forge_web_triggers.values():
                    trigger_orm = await eave_orm.ForgeWebTriggerOrm.upsert(
                        session=db_session,
                        forge_installation_id=installation_orm.id,
                        team_id=installation_orm.team_id,
                        input=trigger,
                    )
                    triggers.append(trigger_orm)

            eave_team = await eave_orm.TeamOrm.one_or_exception(
                session=db_session,
                team_id=installation.team_id,
            )

        eave_team = eave_core.models.Team.from_orm(eave_team)
        forge_integration = eave_core.models.forge.ForgeInstallation.from_orm(installation_orm)
        forge_web_triggers = eave_orm.ForgeWebTriggerOrm.mapping(triggers)

        return eave_api_util.json_response(
            eave_core.operations.forge.QueryForgeInstallation.ResponseBody(
                team=eave_team,
                forge_integration=forge_integration,
                forge_web_triggers=forge_web_triggers,
            )
        )

class UpdateForgeIntegration(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        eave_rutil.get_eave_state(request=request)
        body = await request.json()
        input = eave_core.operations.forge.UpdateForgeInstallation.RequestBody.parse_obj(body)

        async with eave_db.async_session.begin() as db_session:
            installation = await eave_orm.ForgeInstallationOrm.one_or_exception(
                session=db_session,
                forge_app_installation_id=input.forge_integration.forge_app_installation_id,
            )

            eave_team = await eave_orm.TeamOrm.one_or_exception(
                session=db_session,
                team_id=installation.team_id,
            )

            installation.update(
                session=db_session,
                input=input.forge_integration
            )

            if input.forge_web_triggers:
                for trigger in input.forge_web_triggers.values():
                    await eave_orm.ForgeWebTriggerOrm.upsert(
                        session=db_session,
                        team_id=installation.team_id,
                        forge_installation_id=installation.id,
                        input=trigger,
                    )

        # Gets all triggers, including any we just created (`upsert` flushes the transaction)
        triggers = await eave_orm.ForgeWebTriggerOrm.query(
            session=db_session,
            team_id=installation.team_id,
            forge_installation_id=installation.id,
        )

        eave_team = eave_core.models.Team.from_orm(eave_team)
        forge_integration = eave_core.models.forge.ForgeInstallation.from_orm(installation)
        forge_web_triggers = eave_orm.ForgeWebTriggerOrm.mapping(triggers)

        return eave_api_util.json_response(
            eave_core.operations.forge.QueryForgeInstallation.ResponseBody(
                team=eave_team,
                forge_integration=forge_integration,
                forge_web_triggers=forge_web_triggers,
            )
        )