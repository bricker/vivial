from asgiref.typing import HTTPScope
from starlette.requests import Request
from starlette.responses import Response

from eave.core.internal import database
from eave.core.internal.orm.onboarding_submissions import OnboardingSubmissionOrm
from eave.core.internal.orm.team import DashboardAccess, TeamOrm
from eave.stdlib.api_util import json_response
from eave.stdlib.core_api.operations.onboarding_submissions import (
    GetMyOnboardingSubmissionRequest,
    CreateMyOnboardingSubmissionRequest,
)
from eave.stdlib.http_endpoint import HTTPEndpoint
from eave.stdlib.logging import LogContext
from eave.stdlib.util import unwrap


class GetMyOnboardingSubmissionEndpoint(HTTPEndpoint):
    async def handle(self, request: Request, scope: HTTPScope, ctx: LogContext) -> Response:
        async with database.async_session.begin() as db_session:
            eave_team_orm = await TeamOrm.one_or_exception(session=db_session, team_id=unwrap(ctx.eave_authed_team_id))
            onboarding_submission = await OnboardingSubmissionOrm.one_or_exception(
                session=db_session, team_id=unwrap(ctx.eave_authed_team_id)
            )
        return json_response(
            GetMyOnboardingSubmissionRequest.ResponseBody(
                onboarding_submission=onboarding_submission.api_model,
                team=eave_team_orm.api_model,
            )
        )


class CreateMyOnboardingSubmissionEndpoint(HTTPEndpoint):
    async def handle(self, request: Request, scope: HTTPScope, ctx: LogContext) -> Response:
        data = CreateMyOnboardingSubmissionRequest.RequestBody(**(await request.json()))
        async with database.async_session.begin() as db_session:
            eave_team_orm = await TeamOrm.one_or_exception(session=db_session, team_id=unwrap(ctx.eave_authed_team_id))
            onboarding_submission = await OnboardingSubmissionOrm.one_or_none(
                session=db_session, team_id=unwrap(ctx.eave_authed_team_id)
            )

            assert onboarding_submission is None, "Tried to submit multiple onboarding forms"

            onboarding_submission = await OnboardingSubmissionOrm.create(
                session=db_session,
                team_id=eave_team_orm.id,
                response_data=data.form_data,
            )

            eave_team_orm.dashboard_access = (
                DashboardAccess.ALLOW if onboarding_submission.is_qualified() else DashboardAccess.DENY
            )

        return json_response(
            CreateMyOnboardingSubmissionRequest.ResponseBody(
                onboarding_submission=onboarding_submission.api_model,
                team=eave_team_orm.api_model,
            )
        )
