import json
from http import HTTPStatus

import eave.core.internal.database as eave_db
import eave.core.internal.orm as eave_orm
import eave.stdlib.core_api.operations as eave_ops
import fastapi
from eave.stdlib.slack import eave_slack_client

from . import util as eave_request_util

SIGNUPS_SLACK_CHANNEL_ID = "C04HH2N08LD"


async def create_access_request(
    input: eave_ops.CreateAccessRequest.RequestBody, request: fastapi.Request, response: fastapi.Response
) -> fastapi.Response:
    await eave_request_util.validate_signature_or_fail(request=request)

    async with await eave_db.get_session() as session:
        access_request = await eave_orm.AccessRequestOrm.one_or_none(session=session, email=input.email)
        if access_request is not None:
            response.status_code = HTTPStatus.OK
            return response

        access_request = eave_orm.AccessRequestOrm(
            visitor_id=input.visitor_id,
            email=input.email,
            opaque_input=input.opaque_input,
        )

        session.add(access_request)
        await session.commit()

    response.status_code = HTTPStatus.CREATED

    # Notify #sign-ups Slack channel.
    slack_response = await eave_slack_client.chat_postMessage(
        channel=SIGNUPS_SLACK_CHANNEL_ID,
        text="Someone signed up for early access!",
    )

    # because we're passing this through json.loads(), quick prevention of DOS
    if len(input.opaque_input) < 1000:
        jsonoutput = json.dumps(json.loads(input.opaque_input), indent=2)
    else:
        jsonoutput = input.opaque_input

    await eave_slack_client.chat_postMessage(
        channel=SIGNUPS_SLACK_CHANNEL_ID,
        thread_ts=slack_response.get("ts"),
        text=(f"Email: `{input.email}`\n" f"Visitor ID: `{input.visitor_id}`\n" f"```{jsonoutput}```"),
    )

    return response
