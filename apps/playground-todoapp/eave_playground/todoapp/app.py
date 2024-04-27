import json
from http import HTTPStatus
from uuid import UUID

from sqlalchemy import and_, delete, select
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from .orm import TodoListItemOrm, UserOrm, async_session


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
        rendered_json = json.dumps(rendered_todos)

    return Response(content=rendered_json, status_code=HTTPStatus.OK)


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

    rendered_json = json.dumps(todo.render())

    return Response(content=rendered_json, status_code=HTTPStatus.OK)


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


app = Starlette(
    routes=[
        Mount("/static", StaticFiles(directory="eave_playground/todoapp/static")),
        Route(path="/api/todos", methods=["GET"], endpoint=get_todos),
        Route(path="/api/todos", methods=["POST"], endpoint=add_todo),
        Route(path="/api/todos/{todo_id}", methods=["DELETE"], endpoint=delete_todo),
        Route(path="/api/login", methods=["POST"], endpoint=login),
        Route(path="/logout", methods=["GET"], endpoint=logout),
        Route(path="/{rest:path}", methods=["GET"], endpoint=web_app),
    ],
)
