import secrets
from typing import Any

from flask import Flask, Response, jsonify, make_response, render_template, request, redirect, abort
from sqlalchemy import and_, delete, select
from werkzeug.wrappers.response import Response

from .orm import TodoListItemOrm, UserOrm, async_session

app = Flask(__name__)

@app.route("/api/todos", methods=["GET"])
async def get_todos() -> Response:
    user_id = request.cookies.get("user_id")
    if not user_id:
        abort(401)

    async with async_session.begin() as session:
        todos = (await session.scalars(
            select(TodoListItemOrm)
            .where(TodoListItemOrm.user_id == user_id)
            .order_by(TodoListItemOrm.created)
        )).all()

        rendered_todos = [t.render() for t in todos]
        return jsonify(rendered_todos)

@app.route("/api/todos", methods=["POST"])
async def add_todo() -> Response:
    if not request.json:
        raise ValueError("Invalid request body")

    user_id = request.cookies.get("user_id")
    if not user_id:
        abort(401)

    async with async_session.begin() as session:
        todo = TodoListItemOrm(
            user_id=user_id,
            text=request.json["text"],
        )

        session.add(todo)
        await session.flush()

    return jsonify(todo.render())

@app.route("/api/todos/<todo_id>", methods=["DELETE"])
async def delete_todo(todo_id: str) -> Response:
    user_id = request.cookies.get("user_id")
    if not user_id:
        abort(401)

    async with async_session.begin() as session:
        await session.execute(delete(TodoListItemOrm).where(and_(
            TodoListItemOrm.id == todo_id,
            TodoListItemOrm.user_id == user_id
        )))

    return make_response()

@app.route("/api/login", methods=["POST"])
async def login() -> Response:
    if not request.json:
        raise ValueError("Invalid request body")

    async with async_session.begin() as session:
        user = await session.scalar(select(UserOrm).where(UserOrm.username == request.json["username"]))
        if not user:
            user = UserOrm(
                username=request.json["username"],
                visitor_id=request.cookies.get("visitor_id"),
                utm_params=request.cookies.get("utm_params"),
            )
            session.add(user)
            await session.flush()

    response = redirect("/")
    response.set_cookie("user_id", user.id.hex)
    return response

@app.route("/logout", methods=["GET"])
async def logout() -> Response:
    response = redirect(location="/login")
    response.delete_cookie("user_id")

    return response

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path: str) -> str:
    return render_template(
        "index.html.jinja",
    )
