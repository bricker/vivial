from http import HTTPStatus
from uuid import UUID

from fastapi import Request, Response
from starlette.types import ASGIApp, Receive, Scope, Send

from eave.internal.database import session_factory
from eave.internal.orm import TeamOrm


class TeamLookupMiddleware:
    app: ASGIApp

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope)

        team_id = request.headers.get("eave-team-id")
        if team_id is not None:
            async with session_factory() as session:
                team = await TeamOrm.find_one(team_id=UUID(team_id), session=session)

            if team is None:
                response = Response(status_code=HTTPStatus.FORBIDDEN)
                await response(scope, receive, send)
                return

            request.state.team_id = team.id

        await self.app(scope, receive, send)
