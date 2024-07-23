from unittest.mock import patch

from eave.collectors.core.correlation_context import _correlation_context_factory
from eave.collectors.core.correlation_context.async_task import AsyncioCorrelationContext
from eave.collectors.core.correlation_context.thread import ThreadedCorrelationContext

from ..base import BaseTestCase

gunicorn_with_uvicorn_stack = [
    "/eave-monorepo/.venv/lib/python3.12/site-packages/gunicorn/__main__.py",
    "/eave-monorepo/.venv/lib/python3.12/site-packages/gunicorn/app/wsgiapp.py",
    "/eave-monorepo/.venv/lib/python3.12/site-packages/gunicorn/app/base.py",
    "/eave-monorepo/.venv/lib/python3.12/site-packages/gunicorn/app/base.py",
    "/eave-monorepo/.venv/lib/python3.12/site-packages/gunicorn/arbiter.py",
    "/eave-monorepo/.venv/lib/python3.12/site-packages/gunicorn/arbiter.py",
    "/eave-monorepo/.venv/lib/python3.12/site-packages/gunicorn/arbiter.py",
    "/eave-monorepo/.venv/lib/python3.12/site-packages/gunicorn/arbiter.py",
    "/eave-monorepo/.venv/lib/python3.12/site-packages/uvicorn/workers.py",
    "/eave-monorepo/.venv/lib/python3.12/site-packages/gunicorn/workers/base.py",
    "/eave-monorepo/.venv/lib/python3.12/site-packages/gunicorn/workers/base.py",
    "/eave-monorepo/.venv/lib/python3.12/site-packages/gunicorn/app/base.py",
    "/eave-monorepo/.venv/lib/python3.12/site-packages/gunicorn/app/wsgiapp.py",
    "/eave-monorepo/.venv/lib/python3.12/site-packages/gunicorn/app/wsgiapp.py",
    "/eave-monorepo/.venv/lib/python3.12/site-packages/gunicorn/util.py",
    "/.local/share/pyenv/versions/3.12.3/lib/python3.12/importlib/__init__.py",
    "<frozen importlib._bootstrap>",
    "<frozen importlib._bootstrap>",
    "<frozen importlib._bootstrap>",
    "<frozen importlib._bootstrap>",
    "<frozen importlib._bootstrap_external>",
    "<frozen importlib._bootstrap>",
    "/eave-monorepo/apps/playground-quizapp/eave_playground/quizapp/app.py",
    "<frozen importlib._bootstrap>",
    "<frozen importlib._bootstrap>",
    "<frozen importlib._bootstrap>",
    "<frozen importlib._bootstrap_external>",
    "<frozen importlib._bootstrap>",
    "/eave-monorepo/packages/python/eave-collector-openai-py/src/eave/collectors/openai/__init__.py",
    "<frozen importlib._bootstrap>",
    "<frozen importlib._bootstrap>",
    "<frozen importlib._bootstrap>",
    "<frozen importlib._bootstrap_external>",
    "<frozen importlib._bootstrap>",
    "/eave-monorepo/packages/python/eave-collector-openai-py/src/eave/collectors/openai/private/collector.py",
    "<frozen importlib._bootstrap>",
    "<frozen importlib._bootstrap>",
    "<frozen importlib._bootstrap>",
    "<frozen importlib._bootstrap_external>",
    "<frozen importlib._bootstrap>",
    "/eave-monorepo/packages/python/eave-collector-core-py/src/eave/collectors/core/correlation_context/__init__.py",
    "/eave-monorepo/packages/python/eave-collector-core-py/src/eave/collectors/core/correlation_context/__init__.py",
]

gunicorn_default_stack = [
    "<frozen runpy>",
    "<frozen runpy>",
    "/eave-monorepo/.venv/lib/python3.12/site-packages/gunicorn/__main__.py",
    "/eave-monorepo/.venv/lib/python3.12/site-packages/gunicorn/app/wsgiapp.py",
    "/eave-monorepo/.venv/lib/python3.12/site-packages/gunicorn/app/base.py",
    "/eave-monorepo/.venv/lib/python3.12/site-packages/gunicorn/app/base.py",
    "/eave-monorepo/.venv/lib/python3.12/site-packages/gunicorn/arbiter.py",
    "/eave-monorepo/.venv/lib/python3.12/site-packages/gunicorn/arbiter.py",
    "/eave-monorepo/.venv/lib/python3.12/site-packages/gunicorn/arbiter.py",
    "/eave-monorepo/.venv/lib/python3.12/site-packages/gunicorn/arbiter.py",
    "/eave-monorepo/.venv/lib/python3.12/site-packages/gunicorn/workers/base.py",
    "/eave-monorepo/.venv/lib/python3.12/site-packages/gunicorn/workers/base.py",
    "/eave-monorepo/.venv/lib/python3.12/site-packages/gunicorn/app/base.py",
    "/eave-monorepo/.venv/lib/python3.12/site-packages/gunicorn/app/wsgiapp.py",
    "/eave-monorepo/.venv/lib/python3.12/site-packages/gunicorn/app/wsgiapp.py",
    "/eave-monorepo/.venv/lib/python3.12/site-packages/gunicorn/util.py",
    "/.local/share/pyenv/versions/3.12.3/lib/python3.12/importlib/__init__.py",
    "<frozen importlib._bootstrap>",
    "<frozen importlib._bootstrap>",
    "<frozen importlib._bootstrap>",
    "<frozen importlib._bootstrap>",
    "<frozen importlib._bootstrap_external>",
    "<frozen importlib._bootstrap>",
    "/eave-monorepo/apps/playground-quizapp/eave_playground/quizapp/app.py",
    "<frozen importlib._bootstrap>",
    "<frozen importlib._bootstrap>",
    "<frozen importlib._bootstrap>",
    "<frozen importlib._bootstrap_external>",
    "<frozen importlib._bootstrap>",
    "/eave-monorepo/packages/python/eave-collector-openai-py/src/eave/collectors/openai/__init__.py",
    "<frozen importlib._bootstrap>",
    "<frozen importlib._bootstrap>",
    "<frozen importlib._bootstrap>",
    "<frozen importlib._bootstrap_external>",
    "<frozen importlib._bootstrap>",
    "/eave-monorepo/packages/python/eave-collector-openai-py/src/eave/collectors/openai/private/collector.py",
    "<frozen importlib._bootstrap>",
    "<frozen importlib._bootstrap>",
    "<frozen importlib._bootstrap>",
    "<frozen importlib._bootstrap_external>",
    "<frozen importlib._bootstrap>",
    "/eave-monorepo/packages/python/eave-collector-core-py/src/eave/collectors/core/correlation_context/__init__.py",
    "/eave-monorepo/packages/python/eave-collector-core-py/src/eave/collectors/core/correlation_context/__init__.py",
]


class CorrelationContextEngineDetectionTest(BaseTestCase):
    async def test_corr_context_engine_detection_uvicorn_worker(self) -> None:
        self.skipTest("TODO - need to mock the stack")
        with patch("inspect.stack", new_callable=lambda: gunicorn_with_uvicorn_stack):
            engine = _correlation_context_factory()
            assert isinstance(engine, AsyncioCorrelationContext)

    async def test_corr_context_engine_detection_gunicorn_default_worker(self) -> None:
        self.skipTest("TODO - need to mock the stack")
        with patch("inspect.stack", new_callable=lambda: gunicorn_default_stack):
            engine = _correlation_context_factory()
            assert isinstance(engine, ThreadedCorrelationContext)
