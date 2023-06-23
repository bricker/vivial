import os
import alembic
import alembic.config
import alembic.command

EAVE_HOME = os.environ["EAVE_HOME"]
alembic_config = alembic.config.Config("alembic.ini")


def migrate() -> None:
    alembic.command.upgrade(
        revision="head",
        config=alembic_config,
    )
