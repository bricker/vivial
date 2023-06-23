from eave.core.internal import database
from eave.core.internal.orm.connect_installation import ConnectInstallationOrm
from eave.core.internal.orm.team import TeamOrm
from eave.core.internal.orm.confluence_destination import ConfluenceDestinationOrm
from eave.core.public.http_endpoint import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import Response
from eave.stdlib.api_util import json_response
from eave.stdlib.core_api.models.connect import AtlassianProduct
from eave.stdlib.core_api.operations.team import (
    UpsertConfluenceDestinationAuthedRequest,
    GetTeamRequest,
)
from eave.stdlib.request_state import EaveRequestState
from eave.stdlib.util import unwrap


class GetTeamEndpoint(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        eave_state = EaveRequestState.load(request=request)

        async with database.async_session.begin() as db_session:
            eave_team_orm = await TeamOrm.one_or_exception(
                session=db_session, team_id=unwrap(eave_state.ctx.eave_team_id)
            )

            integrations = await eave_team_orm.get_integrations(session=db_session)

        return json_response(
            GetTeamRequest.ResponseBody(
                team=eave_team_orm.api_model,
                integrations=integrations,
            )
        )


class UpsertConfluenceDestinationAuthedEndpoint(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        eave_state = EaveRequestState.load(request=request)
        body = await request.json()
        input = UpsertConfluenceDestinationAuthedRequest.RequestBody.parse_obj(body)

        async with database.async_session.begin() as db_session:
            team = await TeamOrm.one_or_exception(session=db_session, team_id=unwrap(eave_state.ctx.eave_team_id))

            connect_installation = await ConnectInstallationOrm.one_or_exception(
                session=db_session,
                product=AtlassianProduct.confluence,
                team_id=team.id,
            )

            dest = await ConfluenceDestinationOrm.upsert(
                session=db_session,
                team_id=team.id,
                connect_installation_id=connect_installation.id,
                space_key=input.confluence_destination.space_key,
            )

        return json_response(
            UpsertConfluenceDestinationAuthedRequest.ResponseBody(
                team=team.api_model,
                confluence_destination=dest.api_model,
            )
        )
