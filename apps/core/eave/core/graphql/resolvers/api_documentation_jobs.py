from typing import cast

from asgiref.typing import HTTPScope
from eave.core.internal.orm.account import AccountOrm
import eave.stdlib.api_util
import eave.stdlib.util
import eave.core.internal
import eave.core.public
from starlette.requests import Request
from starlette.responses import Response
from eave.stdlib.core_api.operations.account import (
    GetAuthenticatedAccount,
    GetAuthenticatedAccountTeamIntegrations,
)
from eave.stdlib.request_state import EaveRequestState
from eave.stdlib.http_endpoint import HTTPEndpoint

async def get_api_documentation_job(request: Request) -> Response:
    eave_state = EaveRequestState.load(request=request)
    body = await request.json()
    input = GetApiDocumentationJobsOperation.RequestBody.parse_obj(body)

    ids = [job.id for job in jobs] if (jobs := input.jobs) else None

    async with database.async_session.begin() as db_session:
        docs_job_orms = await ApiDocumentationJobOrm.query(
            session=db_session,
            params=ApiDocumentationJobOrm.QueryParams(
                team_id=ensure_uuid(eave_state.ctx.eave_team_id),
                ids=ids,
            ),
        )

    return json_response(
        GetApiDocumentationJobsOperation.ResponseBody(
            jobs=[orm.api_model for orm in list(docs_job_orms)],
        )
    )


async def upsert_api_documentation_job(request: Request) -> Response:
    eave_state = EaveRequestState.load(request=request)
    body = await request.json()
    input = UpsertApiDocumentationJobOperation.RequestBody.parse_obj(body)
    assert eave_state.ctx.eave_team_id, "eave_team_id unexpectedly missing"
    team_id = ensure_uuid(eave_state.ctx.eave_team_id)

    async with database.async_session.begin() as db_session:
        docs_job_orm = await ApiDocumentationJobOrm.one_or_none(
            session=db_session,
            params=ApiDocumentationJobOrm.QueryParams(
                team_id=team_id,
                github_repo_id=input.job.github_repo_id,
            ),
        )

        if docs_job_orm is None:
            docs_job_orm = await ApiDocumentationJobOrm.create(
                session=db_session,
                team_id=team_id,
                github_repo_id=input.job.github_repo_id,
                state=input.job.state,
            )
        else:
            docs_job_orm.update(
                session=db_session,
                state=input.job.state,
                last_result=input.job.last_result,
            )

    return json_response(
        UpsertApiDocumentationJobOperation.ResponseBody(
            job=docs_job_orm.api_model,
        )
    )
