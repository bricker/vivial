import alembic
import alembic.config
import alembic.command

alembic_config = alembic.config.Config("alembic.ini")


def migrate() -> None:
    alembic.command.upgrade(
        revision="head",
        config=alembic_config,
    )
