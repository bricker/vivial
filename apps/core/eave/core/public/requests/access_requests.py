from http import HTTPStatus
import json
import fastapi
import eave.stdlib.core_api.operations as eave_ops
from eave.stdlib.slack import eave_slack_client
import eave.core.internal.database as eave_db
import eave.core.internal.orm as eave_orm
from . import util as eave_request_util

SIGNUPS_SLACK_CHANNEL_ID="C04HH2N08LD"

async def create_access_request(input: eave_ops.CreateAccessRequest.RequestBody, request: fastapi.Request, response: fastapi.Response) -> fastapi.Response:
    await eave_request_util.validate_signature_or_fail(request=request)

    async with await eave_db.get_session() as session:
        access_request = await eave_orm.AccessRequestOrm.one_or_none(session=session, email=input.email)
        if access_request is not None:
            response.status_code = HTTPStatus.OK
            return response

        access_request = eave_orm.AccessRequestOrm(
            visitor_id=input.visitor_id,
            email=input.email,
            opaque_input=json.dumps(input.opaque_input),
        )

        session.add(access_request)
        await session.commit()

    response.status_code = HTTPStatus.CREATED

    # Notify #sign-ups Slack channel.
    slack_response = await eave_slack_client.chat_postMessage(
        channel=SIGNUPS_SLACK_CHANNEL_ID,
        text="Someone signed up for early access!",
    )

    prettyjson = json.dumps(
        input.opaque_input,
        indent=2,
    )
    await eave_slack_client.chat_postMessage(
        channel=SIGNUPS_SLACK_CHANNEL_ID,
        ts=slack_response.get("ts"),
        text=(
            f"Email: `{input.email}`\n"
            f"Visitor ID: `{input.visitor_id}`\n"
            f"```{prettyjson}```"
        ),
    )

    return response
