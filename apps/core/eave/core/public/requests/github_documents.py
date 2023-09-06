from http import HTTPStatus
from eave.core.internal import database
from eave.core.internal.orm.github_documents import GithubDocumentsOrm
from eave.core.public.http_endpoint import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import Response
from eave.stdlib.api_util import json_response
from eave.stdlib.core_api.operations.github_documents import (
    GetGithubReposRequest,
)
from eave.stdlib.request_state import EaveRequestState
from eave.stdlib.util import unwrap, ensure_uuid


class GetGithubDocumentsEndpoint(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        eave_state = EaveRequestState.load(request=request)
        body = await request.json()
        input = GetGithubReposRequest.RequestBody.parse_obj(body)

        # query cant take None values, so we only pass parameters
        # that aren't None by destructuring a dict as kwargs
        kwargs = {k: v for k, v in vars(input.query_params).items() if v is not None}

        async with database.async_session.begin() as db_session:
            gh_doc_orms = await GithubDocumentsOrm.query(
                session=db_session,
                team_id=ensure_uuid(unwrap(eave_state.ctx.eave_team_id)),
                **kwargs,
            )

        return json_response(
            GetGithubReposRequest.ResponseBody(
                documents=[orm.api_model for orm in gh_doc_orms],
            )
        )
