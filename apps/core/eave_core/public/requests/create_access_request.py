from http import HTTPStatus
import json
import fastapi
import eave_stdlib.core_api.operations as eave_ops
import eave_stdlib.slack as eave_slack
import eave_core.internal.database as eave_db
import eave_core.internal.orm as eave_orm
from eave_core.internal.config import app_config

SIGNUPS_SLACK_CHANNEL_ID="C04HH2N08LD"

class CreateAccessRequest:
    @staticmethod
    async def handler(input: eave_ops.CreateAccessRequest.RequestBody, response: fastapi.Response) -> fastapi.Response:
        async with eave_db.session_factory() as session:
            access_request = await eave_orm.AccessRequestOrm.find_one(session=session, email=input.email)

            if access_request is None:
                access_request = eave_orm.AccessRequestOrm(
                    visitor_id=input.visitor_id,
                    email=input.email,
                    opaque_input=json.dumps(input.opaque_input),
                )

                session.add(access_request)
                await session.commit()

                response.status_code = HTTPStatus.CREATED

                # Notify #sign-ups Slack channel.
                slack_client = eave_slack.SlackClient(
                    api_token=app_config.eave_slack_system_bot_token
                )

                slack_response = await slack_client.notify_slack(
                    channel_id=SIGNUPS_SLACK_CHANNEL_ID,
                    text="Someone signed up for early access!",
                )

                prettyjson = json.dumps(
                    input.opaque_input,
                    indent=2,
                )
                await slack_client.notify_slack(
                    channel_id=SIGNUPS_SLACK_CHANNEL_ID,
                    thread_ts=slack_response.get("ts"),
                    text=(
                        f"Email: `{input.email}`\n"
                        f"Visitor ID: `{input.visitor_id}`\n"
                        f"```{prettyjson}```"
                    ),
                )

            else:
                response.status_code = HTTPStatus.OK

        return response
