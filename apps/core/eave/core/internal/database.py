import sqlalchemy
import sqlalchemy.orm
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from .config import app_config

db_uri = sqlalchemy.engine.url.URL.create(
    drivername="postgresql+asyncpg",
    host=app_config.db_host,
    username=app_config.db_user,
    database=app_config.db_name,
)

engine = create_async_engine(db_uri, echo=True)
get_async_session = async_sessionmaker(engine, expire_on_commit=False)
get_sync_session = sqlalchemy.orm.sessionmaker(engine.sync_engine, expire_on_commit=False)
