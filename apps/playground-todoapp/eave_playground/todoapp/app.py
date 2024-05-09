import contextlib
from collections.abc import AsyncGenerator
from http import HTTPStatus
import json
import os
from uuid import UUID

from sqlalchemy import and_, delete, select, update
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse, Response
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from eave.collectors.sqlalchemy import start_eave_sqlalchemy_collector, stop_eave_sqlalchemy_collector

from .orm import TodoListItemOrm, UserOrm, async_engine, async_session


async def get_todos(request: Request) -> Response:
    user_id = request.cookies.get("user_id")
    if not user_id:
        return Response(content=HTTPStatus.UNAUTHORIZED.phrase, status_code=HTTPStatus.UNAUTHORIZED)

    async with async_session.begin() as session:
        result = await session.scalars(
            select(TodoListItemOrm).where(TodoListItemOrm.user_id == user_id).order_by(TodoListItemOrm.created)
        )
        todos = result.all()
        rendered_todos = [t.render() for t in todos]
        return JSONResponse(content=rendered_todos, status_code=HTTPStatus.OK)


async def add_todo(request: Request) -> Response:
    user_id = request.cookies.get("user_id")
    if not user_id:
        return Response(content=HTTPStatus.UNAUTHORIZED.phrase, status_code=HTTPStatus.UNAUTHORIZED)

    body = await request.json()
    async with async_session.begin() as session:
        todo = TodoListItemOrm(
            user_id=UUID(
                user_id
            ),  # Explicit cast to UUID necessary because SQLAlchemy doesn't re-populate this field with the UUID type after commit.
            text=body["text"],
        )

        session.add(todo)

    return JSONResponse(content=todo.render(), status_code=HTTPStatus.OK)


async def delete_todo(request: Request) -> Response:
    user_id = request.cookies.get("user_id")
    if not user_id:
        return Response(content=HTTPStatus.UNAUTHORIZED.phrase, status_code=HTTPStatus.UNAUTHORIZED)

    todo_id = request.path_params["todo_id"]

    async with async_session.begin() as session:
        await session.execute(
            delete(TodoListItemOrm).where(and_(TodoListItemOrm.id == todo_id, TodoListItemOrm.user_id == user_id))
        )

    return Response(status_code=HTTPStatus.OK)


async def update_todo(request: Request) -> Response:
    user_id = request.cookies.get("user_id")
    if not user_id:
        return Response(content=HTTPStatus.UNAUTHORIZED.phrase, status_code=HTTPStatus.UNAUTHORIZED)

    todo_id = request.path_params["todo_id"]

    body = await request.json()
    async with async_session.begin() as session:
        await session.execute(
            update(TodoListItemOrm)
            .where(and_(TodoListItemOrm.id == todo_id, TodoListItemOrm.user_id == user_id))
            .values(text=body["text"])
        )

    return Response(status_code=HTTPStatus.OK)


async def login(request: Request) -> Response:
    body = await request.json()
    username = body["username"]

    async with async_session.begin() as session:
        user = await session.scalar(select(UserOrm).where(UserOrm.username == username))
        if not user:
            user = UserOrm(
                username=username,
                visitor_id=request.cookies.get("visitor_id"),
                utm_params=request.cookies.get("utm_params"),
            )
            session.add(user)
            await session.commit()

        response = Response(status_code=HTTPStatus.OK)
        response.set_cookie("user_id", user.id.hex)
        response.set_cookie("user_name", user.username)

    return response


def logout(request: Request) -> Response:
    response = RedirectResponse(url="/login")
    response.delete_cookie("user_id")
    return response


templates = Jinja2Templates(directory="eave_playground/todoapp/templates")


def web_app(request: Request) -> Response:
    response = templates.TemplateResponse(request, "index.html.jinja")
    return response


def status_endpoint(request: Request) -> Response:
    # This doesn't use the shared status_endpoint function, because this app deliberately doesn't use the eave stdlib.
    body = {
        "service": os.getenv("GAE_SERVICE", "unknown"),
        "version": os.getenv("GAE_VERSION", "unknown"),
        "release_date": os.getenv("GAE_RELEASE_DATE", "unknown"),
        "status": "OK",
    }

    response = JSONResponse(content=body, status_code=HTTPStatus.OK)
    return response

def health_endpoint(request: Request) -> Response:
    return Response(content="1", status_code=HTTPStatus.OK)

@contextlib.asynccontextmanager
async def lifespan(app: Starlette) -> AsyncGenerator[None, None]:
    await start_eave_sqlalchemy_collector(engine=async_engine)
    yield
    stop_eave_sqlalchemy_collector()


app = Starlette(
    routes=[
        Mount("/static", StaticFiles(directory="eave_playground/todoapp/static")),
        Route(path="/status", methods=["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"], endpoint=status_endpoint),
        Route(path="/healthz", methods=["GET"], endpoint=health_endpoint),
        Route(path="/api/todos", methods=["GET"], endpoint=get_todos),
        Route(path="/api/todos", methods=["POST"], endpoint=add_todo),
        Route(path="/api/todos/{todo_id}", methods=["DELETE"], endpoint=delete_todo),
        Route(path="/api/todos/{todo_id}", methods=["PATCH"], endpoint=update_todo),
        Route(path="/api/login", methods=["POST"], endpoint=login),
        Route(path="/logout", methods=["GET"], endpoint=logout),
        Route(path="/{rest:path}", methods=["GET"], endpoint=web_app),
    ],
    lifespan=lifespan,
)
