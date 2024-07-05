import contextlib
import random
import json
import logging
import os
from collections.abc import AsyncGenerator
from http import HTTPStatus
from textwrap import dedent
from uuid import UUID

import google.cloud.logging
from openai import AsyncOpenAI
from openai.types.chat.completion_create_params import ResponseFormat
from sqlalchemy import and_, delete, select, update
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse, Response
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates



_COOKIE_PREFIX = "quizapp."
_VISITOR_ID_COOKIE_NAME = f"{_COOKIE_PREFIX}visitor_id"
_UTM_PARAMS_COOKIE_NAME = f"{_COOKIE_PREFIX}utm_params"

if os.getenv("EAVE_ENV", "development") == "production":
    # https://cloud.google.com/python/docs/reference/logging/latest/std-lib-integration
    _gcp_log_client = google.cloud.logging.Client()
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    _gcp_log_client.setup_logging(log_level=logging.getLevelNamesMapping().get(log_level) or logging.INFO)

_openai_client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

topics = [
    "pop culture",
    "movies",
    "TV",
    "history",
    "geography",
    "technology",
    "music",
    "the beatles",
    "art",
    "the decades (eg 90's, 80's, etc)",
    "the 2000's",
    "the 90's",
    "the 80's",
    "the 70's",
    "the 60's",
    "the 50's",
    "the 40's",
    "the 30's",
    "the 20's",
    "world war 2",
    "world war 1",
    "the US civil war",
    "the united states",
    "countries",
    "world history",
    "US history",
    "video games",
    "literature",
    "space",
    "religion",
    "language",
    "vocabulary",
    "food",
    "animals",
    "celebrities",
    "musicians",
    "math",
    "physics",
    "electronics",
    "electricity",
    "programming",
    "programming languages",
    "javascript programming language",
    "python programming language",
    "java programming language",
    "c programming language",
    "ruby programming language",
    "typescript programming language",
    "bash scripting",
    "linux",
    "biology",
    "politics",
    "US presidents",
]

async def get_quiz(request: Request) -> Response:
    quiz_topic = random.choice(topics)  # noqa: S311

    chat_completion = await _openai_client.chat.completions.create(
        temperature=0,
        frequency_penalty=0,
        max_tokens=4096,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": dedent("""
                Your purpose is to generate fun, daily quizzes and trivia for people to test their knowledge of different topics.
                Each quiz has a topic and a list of questions.
                You are known for creating unique questions, such that your quizzes are never repetitive, even for the same topic.
                """),
            },
            {
                "role": "user",
                "content": dedent(f"""
                Generate a multiple-choice quiz with 10 questions. For each question, provide 4 choices for the answer, in random order: three incorrect answers, and one correct answer.

                The topic of the quiz is: "{quiz_topic}"

                Respond with a JSON object with the following schema:

                ===
                {{
                    "title": "<quiz title>",
                    "questions": [
                        {{
                            "text": "<question text>",
                            "choices": [
                                "<choice text 1>",
                                "<choice text 2>",
                                "<choice text 3>",
                                "<choice text 4>"
                            ],
                            "correct_answer_index": <integer array index of the correct choice>
                        }},
                        {{ <question 2> }},
                        {{ <question 3> }},
                        ...
                        {{ <question 10> }},
                }}
                ===
                """),
            },
        ],
        model="gpt-4o",
    )

    content = chat_completion.choices[0].message.content
    if content:
        jcontent = json.loads(content)

        # Shuffle the choices.
        for question in jcontent["questions"]:
            correct_choice = question["choices"][question["correct_answer_index"]]
            random.shuffle(question["choices"])
            question["correct_answer_index"] = next(i for i, c in enumerate(question["choices"]) if c == correct_choice)
        return JSONResponse(content=jcontent, status_code=HTTPStatus.OK)
    else:
        return Response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)



templates = Jinja2Templates(directory="eave_quiz/quizapp/templates")


def web_app(request: Request) -> Response:
    response = templates.TemplateResponse(
        request=request,
        name="index.html.jinja",
        context={
            "EAVE_CLIENT_ID": os.getenv("PLAYGROUND_QUIZAPP_EAVE_CLIENT_ID"),
            "COLLECTOR_ASSET_BASE": os.getenv("COLLECTOR_ASSET_BASE", "https://storage.googleapis.com/cdn.eave.dev"),
        },
    )
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


app = Starlette(
    routes=[
        Mount("/static", StaticFiles(directory="eave_quiz/quizapp/static")),
        Route(path="/status", methods=["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"], endpoint=status_endpoint),
        Route(path="/healthz", methods=["GET"], endpoint=health_endpoint),
        Route(path="/api/quiz", methods=["GET"], endpoint=get_quiz),
        Route(path="/{rest:path}", methods=["GET"], endpoint=web_app),
    ],
)


# StarletteCollectorManager.start(app)
