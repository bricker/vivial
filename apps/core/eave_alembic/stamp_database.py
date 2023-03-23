from dotenv import load_dotenv

load_dotenv()

from alembic import command
from alembic.config import Config

alembic_config = Config("alembic.ini")
command.stamp(alembic_config, "head")
