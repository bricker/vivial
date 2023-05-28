import asyncio
import json
from typing import Any, Coroutine, Optional, TypeVar
import uuid
from google.cloud import tasks
from starlette.requests import Request
import eave.stdlib
import eave.stdlib.requests
from eave.stdlib.eave_origins import EaveOrigin
from eave.stdlib.headers import (
    EAVE_ORIGIN_HEADER,
    EAVE_REQUEST_ID_HEADER,
    EAVE_SIGNATURE_HEADER,
    GCP_CLOUD_TRACE_CONTEXT,
    GCP_GAE_REQUEST_LOG_ID,
)

from .typing import JsonObject
from .config import shared_config
from .logging import LogContext, eaveLogger

T = TypeVar("T")

asyncio_tasks = set[asyncio.Task[Any]]()


def do_in_background(coro: Coroutine[Any, Any, T]) -> asyncio.Task[T]:
    task = asyncio.create_task(coro)
    asyncio_tasks.add(task)
    task.add_done_callback(asyncio_tasks.discard)
    return task


async def get_queue(queue_name: str) -> tasks.Queue:
    client = tasks.CloudTasksAsyncClient()

    queue = client.queue_path(
        project=shared_config.google_cloud_project,
        location=shared_config.app_location,
        queue=queue_name,
    )

    queue = await client.get_queue(name=queue)
    return queue


async def create_task_from_request(
    queue_name: str,
    target_path: str,
    request: Request,
    origin: EaveOrigin,
    unique_task_id: Optional[str] = None,
    task_name_prefix: Optional[str] = None,
    ctx: Optional[LogContext] = None,
) -> None:
    if not unique_task_id:
        if trace_id := request.headers.get(GCP_CLOUD_TRACE_CONTEXT):
            unique_task_id = trace_id.split("/")[0]
        elif log_id := request.headers.get(GCP_GAE_REQUEST_LOG_ID):
            unique_task_id = log_id

    if unique_task_id and task_name_prefix:
        unique_task_id = f"{task_name_prefix}{unique_task_id}"

    payload = await request.body()
    headers = dict(request.headers)

    # The "user agent" is Slack Bot when coming from Slack, but for the task processor that's not the case.
    headers.pop("user-agent", None)

    await create_task(
        queue_name=queue_name,
        target_path=target_path,
        payload=payload,
        origin=origin,
        unique_task_id=unique_task_id,
        headers=headers,
        ctx=ctx,
    )

async def create_task(
    queue_name: str,
    target_path: str,
    payload: JsonObject | bytes,
    origin: EaveOrigin,
    unique_task_id: Optional[str] = None,
    headers: Optional[dict[str, str]] = None,
    ctx: Optional[LogContext] = None,
) -> tasks.Task:
    ctx = LogContext.wrap(ctx)

    if isinstance(payload, dict):
        # FIXME: Encrypt this; it's visible as plaintext in Cloud Tasks
        body = json.dumps(payload).encode()
    else:
        body = payload

    if not headers:
        headers = {}

    # Slack already sets this for the incoming event request, but setting it here too to be explicit.
    headers["content-type"] = "application/json"

    request_id = ctx.getset("request_id", str(uuid.uuid4()))
    signature_message = eave.stdlib.requests.build_message_to_sign(
        method="POST",
        origin=origin.value,
        request_id=request_id,
        url=target_path,
        payload=body.decode(),
        team_id=None,
        account_id=None,
    )

    signature = eave.stdlib.signing.sign_b64(signing_key=eave.stdlib.signing.get_key(origin), data=signature_message)

    headers[EAVE_SIGNATURE_HEADER] = signature
    headers[EAVE_REQUEST_ID_HEADER] = request_id
    headers[EAVE_ORIGIN_HEADER] = origin.value

    client = tasks.CloudTasksAsyncClient()

    parent = client.queue_path(
        project=shared_config.google_cloud_project,
        location=shared_config.app_location,
        queue=queue_name,
    )

    task = tasks.Task(
        app_engine_http_request=tasks.AppEngineHttpRequest(
            http_method=tasks.HttpMethod.POST,
            relative_uri=target_path,
            headers=headers,
            body=body,
        )
    )

    if unique_task_id:
        # If this isn't given, Cloud Tasks creates a unique task name automatically.
        task_name = client.task_path(
            project=shared_config.google_cloud_project,
            location=shared_config.app_location,
            queue=queue_name,
            task=unique_task_id,
        )
        task.name = task_name
    else:
        task_name = None

    eaveLogger.debug(
        f"Creating task on queue {queue_name}",
        extra=ctx.set(
            {
                "task_name": task_name,
                "queue_name": parent,
                "eave_headers": headers,
            }
        ),
    )

    t = await client.create_task(parent=parent, task=task)
    return t
