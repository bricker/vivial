from dataclasses import dataclass
from datetime import datetime
from http import HTTPStatus
from typing import Any, cast
from uuid import UUID

from aiohttp.hdrs import AUTHORIZATION
from asgiref.typing import HTTPScope

from eave.core.internal import database
from eave.core.internal.clickhouse import clickhouse_client
from eave.core.internal.clickhouse.dbchanges import DatabaseChangesTableHandle
from eave.core.internal.config import CORE_API_APP_CONFIG
from eave.core.internal.orm.client_credentials import ClientCredentialsOrm, ClientScope
from eave.core.internal.orm.github_installation import GithubInstallationOrm
from eave.core.internal.orm.github_repos import GithubRepoOrm
from eave.monitoring.datastructures import DataIngestRequestBody, DatabaseChangeEventPayload, EventType, RawEvent
from eave.stdlib.analytics import log_event
from eave.stdlib.api_util import get_bearer_token, get_header_value_or_exception, json_response
from eave.stdlib.config import GITHUB_EVENT_QUEUE_NAME
from eave.stdlib.core_api.models.github_repos import (
    GithubRepoFeature,
    GithubRepoFeatureState,
)
from eave.stdlib.core_api.operations.github_repos import (
    CreateGithubRepoRequest,
    DeleteGithubReposRequest,
    FeatureStateGithubReposRequest,
    GetAllTeamsGithubReposRequest,
    GetGithubReposRequest,
    UpdateGithubReposRequest,
)
from eave.stdlib.eave_origins import EaveApp
from eave.stdlib.exceptions import ForbiddenError, UnauthorizedError
from eave.stdlib.github_api.models import GithubRepoInput
from eave.stdlib.github_api.operations.tasks import RunApiDocumentationTask
from eave.stdlib.headers import EAVE_CLIENT_ID, EAVE_CLIENT_SECRET, EAVE_REQUEST_ID_HEADER, EAVE_TEAM_ID_HEADER
from eave.stdlib.http_endpoint import HTTPEndpoint
from eave.stdlib.logging import LogContext
from eave.stdlib.request_state import EaveRequestState
from eave.stdlib.task_queue import create_task
from eave.stdlib.util import b64decode, ensure_uuid, unwrap
from starlette.requests import Request
from starlette.responses import Response


class DataIngestionEndpoint(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        body = await request.json()
        input = DataIngestRequestBody.from_json(data=body)

        http_scope = cast(HTTPScope, request.scope)

        # TODO: Move client credentials validation into middleware
        client_id = get_header_value_or_exception(scope=http_scope, name=EAVE_CLIENT_ID)
        client_secret = get_header_value_or_exception(scope=http_scope, name=EAVE_CLIENT_SECRET)

        async with database.async_session.begin() as db_session:
            creds = (await ClientCredentialsOrm.query(
                session=db_session,
                params=ClientCredentialsOrm.QueryParams(
                    id=ensure_uuid(client_id),
                    secret=client_secret,
                )
            )).one_or_none()

            if not creds:
                raise UnauthorizedError("invalid credentials")

            if ClientScope.write not in creds.scopes:
                raise ForbiddenError("invalid scopes")

            await creds.touch(session=db_session)

        match input.event_type:
            case EventType.dbchange:
                handle = DatabaseChangesTableHandle(team_id=creds.team_id)

        await handle.insert(events=input.events)

        response = Response(content="OK", status_code=200)
        return response
