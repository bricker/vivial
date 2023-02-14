"""empty message

Revision ID: ed5f3e3e365d
Revises: 61e675d9dc13
Create Date: 2023-01-22 13:37:02.305166

"""

import os
from dotenv import load_dotenv

from eave.public.shared import DocumentPlatform
load_dotenv()

from alembic import op
import sqlalchemy as sa
from sqlalchemy import orm
import eave.internal.orm as eorm

# revision identifiers, used by Alembic.
revision = 'ed5f3e3e365d'
down_revision = '61e675d9dc13'
branch_labels = None
depends_on = '61e675d9dc13'


def upgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    newteam = eorm.TeamOrm(
        name="Eave",
        document_platform=DocumentPlatform.confluence,
    )
    session.add(newteam)
    session.commit()

    cd = eorm.ConfluenceDestinationOrm(
        team_id=newteam.id,
        url="https://eave-fyi.atlassian.net",
        api_username="bryan@eave.fyi",
        api_key=os.environ["CONFLUENCE_API_KEY"],
        space="EAVE",
    )

    session.add(cd)
    session.commit()

def downgrade() -> None:
    pass

