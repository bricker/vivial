# import json
# import random
# import urllib.parse
# from uuid import UUID
# import uuid
# import mockito
# from typing import Any, AsyncGenerator, Awaitable, Callable, Generator, Optional, Protocol, TypeVar
# from httpx import AsyncClient, Response
# import pytest
# from sqlalchemy import literal_column, func as safunc, select
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.orm import Mapped
# import eave.core.app
# from eave.core.internal.config import app_config
# import eave.core.internal.database as eave_db
# import eave.core.internal.orm as eave_orm
# import eave.stdlib.core_api.models as eave_models
# import eave.stdlib.util as eave_util
# import eave.stdlib.jwt as eave_jwt
# import eave.stdlib.signing as eave_signing
# from eave.stdlib.eave_origins import EaveOrigin

# eave_db.engine.echo = False

# TEST_SIGNING_KEY = eave_signing.SigningKeyDetails(
#     id="test-key",
#     version="1",
#     algorithm=eave_signing.SigningAlgorithm.RS256,
# )

# class AnyStandardOrm(Protocol):
#     id: Mapped[UUID]

# T = TypeVar("T")
# J = TypeVar("J", bound=AnyStandardOrm)

# @pytest.fixture
# def test_data() -> dict[str, Any]:
#     return dict[str, Any]()

# @pytest.fixture
# async def http_client() -> AsyncGenerator[AsyncClient, None]:
#     client = AsyncClient(app=eave.core.app.app, base_url=app_config.eave_api_base)
#     yield client
#     await client.aclose()

# @pytest.fixture
# async def db_session() -> AsyncGenerator[AsyncSession, None]:
#     session = eave_db.get_async_session()
#     session.begin()
#     connection = await session.connection()
#     assert connection.engine.url.database != "eave"
#     await connection.run_sync(eave_orm.Base.metadata.drop_all)
#     await connection.run_sync(eave_orm.Base.metadata.create_all)
#     yield session
#     await session.close()

# @pytest.fixture
# def http_request(http_client: AsyncClient) -> Callable[..., Awaitable[Response]]:
#     async def _http_request(
#         url: str,
#         payload: Optional[eave_util.JsonObject] = None,
#         method: str = "POST",
#         headers: dict[str, str] = {},
#         access_token: Optional[eave_jwt.JWT] = None,
#         **kwargs: Any
#     ) -> Response:
#         request_args: dict[str, Any] = {}

#         if payload is not None:
#             if method == "GET":
#                 data = urllib.parse.urlencode(query=payload)
#                 request_args["params"] = data
#             else:
#                 data = json.dumps(payload)
#                 request_args["content"] = data

#             if (team_id := headers.get("eave-team-id")) is not None:
#                 headers["eave-team-id"] = team_id

#             headers["eave-signature"] = eave_signing.sign_b64(signing_key=TEST_SIGNING_KEY, data=data)
#             headers["eave-origin"] = EaveOrigin.eave_www.value

#             if access_token:
#                 headers["authorization"] = f"Bearer {access_token.to_str()}"

#         response = await http_client.request(
#             method,
#             url,
#             headers=headers,
#             **request_args,
#             **kwargs,
#         )

#         return response

#     return _http_request

# class DatabaseOperations:
#     db_session: AsyncSession

#     def __init__(self, db_session: AsyncSession) -> None:
#         self.db_session = db_session

#     async def save(self, obj: J) -> J:
#         self.db_session.add(obj)
#         await self.db_session.commit()
#         return obj

#     async def reload(self, obj: J) -> J | None:
#         stmt = select(obj.__class__).where(literal_column("id") == obj.id)
#         result = await self.db_session.scalar(stmt)
#         return result

#     async def delete(self, obj: AnyStandardOrm) -> None:
#         await self.db_session.delete(obj)

#     async def count(self, cls: AnyStandardOrm) -> int:
#         query = select(safunc.count(cls.id))
#         count = await self.db_session.scalar(query)
#         if count is None:
#             count = 0
#         return count

# @pytest.fixture
# def db_ops(db_session: AsyncSession) -> DatabaseOperations:
#     return DatabaseOperations(db_session=db_session)

# @pytest.fixture
# def unwrap(value: Optional[T]) -> Callable[..., T]:
#     def _inner() -> T:
#         assert value is not None
#         return value
#     return _inner

# @pytest.fixture
# def anystring(test_data: dict[str, Any]) -> Callable[..., str]:
#     def _inner(name: str) -> str:
#         if name not in test_data:
#             data = str(uuid.uuid4())
#             test_data[name] = data

#         value: str = test_data[name]
#         return value
#     return _inner

# @pytest.fixture
# def anyuuid(test_data: dict[str, Any]) -> Callable[..., UUID]:
#     def _inner(name: str) -> UUID:
#         if name not in test_data:
#             data = uuid.uuid4()
#             test_data[name] = data

#         value: uuid.UUID = test_data[name]
#         return value
#     return _inner

# @pytest.fixture
# def anyint(test_data: dict[str, Any]) -> Callable[..., int]:
#     def _inner(name: str) -> int:
#         if name not in test_data:
#             data = random.randint(0, 9999)
#             test_data[name] = data

#         value: int = test_data[name]
#         return value
#     return _inner

# @pytest.fixture
# async def team(db_ops: DatabaseOperations, anystring: Callable[..., str]) -> eave_orm.TeamOrm:
#     team = eave_orm.TeamOrm(name=anystring("team name"))
#     await db_ops.save(team)
#     return team

# @pytest.fixture
# async def account(team: eave_orm.TeamOrm, db_ops: DatabaseOperations, anystring: Callable[..., str], **kwargs: Any) -> eave_orm.AccountOrm:
#     account = eave_orm.AccountOrm(
#         auth_provider=kwargs.get("auth_provider", eave_models.AuthProvider.slack),
#         auth_id=kwargs.get("auth_id", anystring("auth_id")),
#         oauth_token=kwargs.get("oauth_token", anystring("oauth_token")),
#         team_id=team.id,
#     )
#     await db_ops.save(account)
#     return account

# @pytest.fixture(autouse=True)
# def test_setup() -> None:
#     pass

# @pytest.fixture(autouse=True)
# def test_teardown() -> None:
#     mockito.verifyStubbedInvocationsAreUsed()
#     mockito.unstub()
