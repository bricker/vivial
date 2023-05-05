import json
from http import HTTPStatus

import eave.core.internal.database as eave_db
import eave.stdlib.core_api.operations as eave_ops
import fastapi
from eave.core.internal.orm.access_request import AccessRequestOrm
import eave.stdlib.slack
import eave.core.public.requests

SIGNUPS_SLACK_CHANNEL_ID = "C04HH2N08LD"


async def create_access_request(
    input: eave_ops.CreateAccessRequest.RequestBody, request: fastapi.Request, response: fastapi.Response
) -> fastapi.Response:
    eave_state = eave.core.public.requests.eave_request_util.get_eave_state(request=request)
    async with eave_db.async_session.begin() as db_session:
        access_request = await AccessRequestOrm.one_or_none(session=db_session, email=input.email)
        if access_request is not None:
            response.status_code = HTTPStatus.OK
            return response

        access_request = AccessRequestOrm(
            visitor_id=input.visitor_id,
            email=input.email,
            opaque_input=input.opaque_input,
        )

        db_session.add(access_request)

    response.status_code = HTTPStatus.CREATED

    try:
        slack_client = eave.stdlib.slack.get_authenticated_eave_system_slack_client()
        # Notify #sign-ups Slack channel.
        slack_response = await slack_client.chat_postMessage(
            channel=SIGNUPS_SLACK_CHANNEL_ID,
            text="Someone signed up for early access!",
        )

        # because we're passing this through json.loads(), quick prevention of DOS
        if len(input.opaque_input) < 1000:
            jsonoutput = json.dumps(json.loads(input.opaque_input), indent=2)
        else:
            jsonoutput = input.opaque_input

        await slack_client.chat_postMessage(
            channel=SIGNUPS_SLACK_CHANNEL_ID,
            thread_ts=slack_response.get("ts"),
            text=(f"Email: `{input.email}`\n" f"Visitor ID: `{input.visitor_id}`\n" f"```{jsonoutput}```"),
        )
    except Exception as e:
        eave.stdlib.logger.error("Error while sending message to Slack channel.", exc_info=e, extra=eave_state.log_context)

    return response
