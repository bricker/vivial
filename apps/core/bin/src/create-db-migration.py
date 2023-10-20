import os
import sys
import click
from eave.dev_tooling.dotenv_loader import load_standard_dotenv_files
import alembic
import alembic.config
import alembic.command

sys.path.append('.')

alembic_config = alembic.config.Config("alembic.ini")
load_standard_dotenv_files()

@click.command()
@click.option("-m", "--message", required=True)
def create_revision(message: str) -> None:
    alembic.command.revision(
        config=alembic_config,
        message=message,
        autogenerate=True,
    )

if __name__ == "__main__":
    create_revision()
