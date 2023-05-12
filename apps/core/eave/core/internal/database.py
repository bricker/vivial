import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.util
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from .config import app_config

db_uri = sqlalchemy.engine.url.URL.create(
    drivername="postgresql+asyncpg",
    host=app_config.db_host,
    username=app_config.db_user,
    password=app_config.db_pass,
    database=app_config.db_name,
)
async_engine = create_async_engine(db_uri, echo=app_config.dev_mode)


# db_driver = "postgresql+asyncpg://"
# async_engine = create_async_engine(db_driver, echo=app_config.dev_mode)
# connector = Connector()

# # @event.listens_for(async_engine.sync_engine, "do_connect")
# # def get_connection(dialect: sqlalchemy.engine.Dialect, conn_rec: sqlalchemy.pool.ConnectionPoolEntry, cargs: tuple[Any, ...], cparams: dict[str, Any]) -> DBAPIConnection:
# def get_connection() -> asyncpg.connection.Connection:
#     """
#     If app_config.db_host is set ("EAVE_DB_HOST"), then we'll use that.
#     This is useful for either connecting to a locally-running database, or for connecting to a locally-running
#     Cloud SQL Auth Proxy.

#     If EAVE_DB_HOST isn't set, then we'll use the Google Cloud SQL Connector, which is basically an in-process
#     Cloud SQL Auth Proxy, and therefore more portable. Also, required in order use IAM auth in App Engine.
#     """
#     connection: asyncpg.connection.Connection

#     if app_config.db_host:
#         connection = dialect.connect(
#             host=app_config.db_host,
#             user=app_config.db_user,
#             password=app_config.db_pass,
#             database=app_config.db_name,
#         )

#     else:
#     connection: asyncpg.connection.Connection = connector.connect(
#         app_config.cloudsql_connection_string,
#         "asyncpg",
#         user=app_config.db_user,
#         db=app_config.db_name,
#         password=app_config.db_pass,
#         enable_iam_auth=True,
#     )

#     # connection = sqlalchemy.util.await_fallback(coro)
#     return connection


sync_session = sqlalchemy.orm.sessionmaker(async_engine.sync_engine, expire_on_commit=False)
"""
:class:`sqlalchemy.orm.Session` factory. Use with `begin()` to automatically
commit and close the session when the context manager exits.

Example::

    with eave_db.sync_session.begin() as db_session:
        db_session.add(some_object)

    print("session is automatically committed, some_object has been persisted.")
"""

async_session = async_sessionmaker(async_engine, expire_on_commit=False)
"""
:class:`sqlalchemy.ext.asyncio.AsyncSession` factory. Use with `begin()` to automatically
commit and close the session when the context manager exits.

Example::

    async with eave_db.async_session.begin() as db_session:
        db_session.add(some_object)

    print("session is automatically committed, some_object has been persisted.")
"""
