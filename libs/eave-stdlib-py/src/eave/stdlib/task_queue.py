

import asyncio
import json
from typing import Any, Coroutine, Mapping, Optional, TypeVar
from google.cloud import tasks
from starlette.requests import Request

from eave.stdlib.typing import JsonObject
from .config import shared_config

T = TypeVar("T")

asyncio_tasks = set[asyncio.Task[Any]]()


def do_in_background(coro: Coroutine[Any, Any, T]) -> asyncio.Task[T]:
    task = asyncio.create_task(coro)
    asyncio_tasks.add(task)
    task.add_done_callback(asyncio_tasks.discard)
    return task


client = tasks.CloudTasksAsyncClient()

async def create_task_from_request(queue_name: str, target_path: str, request: Request, unique_task_id: Optional[str] = None) -> None:
    if not unique_task_id:
        unique_task_id = request.headers.get("X-Cloud-Trace-Context")

    payload = await request.body()
    headers = request.headers
    await create_task(
        queue_name=queue_name,
        target_path=target_path,
        payload=payload,
        unique_task_id=unique_task_id,
        headers=headers
    )

async def create_task(queue_name: str, target_path: str, payload: JsonObject | bytes, unique_task_id: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> tasks.Task:
    if isinstance(payload, dict):
        body = json.dumps(payload).encode()
    else:
        body = payload

    if not headers:
        headers = {}

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

    t = await client.create_task(parent=parent, task=task)
    return t