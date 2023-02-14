import os
from typing import Optional

import sqlalchemy
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from eave.internal.settings import APP_SETTINGS

if APP_SETTINGS.db_connection_string is not None:
    db_uri = sqlalchemy.make_url(APP_SETTINGS.db_connection_string)
else:
    assert APP_SETTINGS.db_driver is not None

    db_uri = sqlalchemy.engine.url.URL.create(
        drivername=APP_SETTINGS.db_driver,
        host=APP_SETTINGS.db_host,
        port=APP_SETTINGS.db_port,
        username=APP_SETTINGS.db_user,
        password=APP_SETTINGS.db_pass,
        database=APP_SETTINGS.db_name,
    )

engine = create_async_engine(db_uri, echo=True)

session_factory = async_sessionmaker(engine, expire_on_commit=False)
