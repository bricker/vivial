from asgiref.typing import HTTPScope
from starlette.requests import Request
from starlette.responses import Response

from eave.core.internal import database
from eave.core.internal.orm.onboarding_submissions import OnboardingSubmissionOrm
from eave.core.internal.orm.team import TeamOrm
from eave.stdlib.api_util import json_response
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.core_api.operations.onboarding_submissions import (
    CreateMyOnboardingSubmissionRequest,
    GetMyOnboardingSubmissionRequest,
)
from eave.stdlib.http_endpoint import HTTPEndpoint
from eave.stdlib.logging import LOGGER, LogContext
from eave.stdlib.slack import get_authenticated_eave_system_slack_client
from eave.stdlib.util import unwrap


class GetMyOnboardingSubmissionEndpoint(HTTPEndpoint):
    async def handle(self, request: Request, scope: HTTPScope, ctx: LogContext) -> Response:
        async with database.async_session.begin() as db_session:
            eave_team_orm = await TeamOrm.one_or_exception(session=db_session, team_id=unwrap(ctx.eave_authed_team_id))
            onboarding_submission = await OnboardingSubmissionOrm.one_or_none(
                session=db_session, team_id=unwrap(ctx.eave_authed_team_id)
            )
        return json_response(
            GetMyOnboardingSubmissionRequest.ResponseBody(
                onboarding_submission=onboarding_submission.api_model if onboarding_submission else None,
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
                submission=data.onboarding_submission,
            )

            eave_team_orm.dashboard_access = onboarding_submission.is_qualified()

        try:
            # TODO: This should happen in a pubsub subscriber for better performance.
            # Notify #sign-ups Slack channel.

            channel_id = SHARED_CONFIG.eave_slack_signups_channel_id
            slack_client = get_authenticated_eave_system_slack_client()

            if slack_client and channel_id:
                slack_response = await slack_client.chat_postMessage(
                    channel=channel_id,
                    text="Someone completed onboarding!",
                )

                await slack_client.chat_postMessage(
                    channel=channel_id,
                    thread_ts=slack_response.get("ts"),
                    text=(
                        f"Team ID: `{eave_team_orm.id}`\n"
                        f"Eave Team Name: `{eave_team_orm.name}`\n"
                        f"```\n{data.onboarding_submission.json()}\n```"
                    ),
                )
        except Exception as e:
            LOGGER.exception(e, ctx)

        return json_response(
            CreateMyOnboardingSubmissionRequest.ResponseBody(
                onboarding_submission=onboarding_submission.api_model,
                team=eave_team_orm.api_model,
            )
        )
