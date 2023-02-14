"""empty message

Revision ID: 1e230897fd34
Revises: ed5f3e3e365d
Create Date: 2023-01-22 14:11:09.557288

"""
from datetime import datetime
import enum
import os
from uuid import UUID, uuid4
from dotenv import load_dotenv
load_dotenv()

from eave.public.shared import DocumentPlatform, SubscriptionSourceEvent, SubscriptionSourcePlatform

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Unicode, UnicodeText, all_, orm, select
import eave.internal.orm as eorm

# revision identifiers, used by Alembic.
revision = '1e230897fd34'
down_revision = 'ed5f3e3e365d'
branch_labels = None
depends_on = 'ed5f3e3e365d'

class DocumentOrm(eorm.Base):
    __tablename__ = "documents"

    id: orm.Mapped[UUID] = orm.mapped_column(primary_key=True, default=uuid4)
    external_url: orm.Mapped[str] = orm.mapped_column(nullable=True, index=True)
    external_id: orm.Mapped[str] = orm.mapped_column(nullable=True, index=True)
    title: orm.Mapped[str] = orm.mapped_column(Unicode, nullable=False)
    content: orm.Mapped[str] = orm.mapped_column(UnicodeText, nullable=False)
    created: orm.Mapped[datetime] = orm.mapped_column(nullable=False, default=datetime.utcnow)
    updated: orm.Mapped[datetime] = orm.mapped_column(nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

class SlackSourceType(enum.Enum):
    message = 'message'

class SlackSubscriptionOrm(eorm.Base):
    __tablename__ = "slack_subscriptions"

    id: orm.Mapped[UUID] = orm.mapped_column(primary_key=True, default=uuid4)
    document_id: orm.Mapped[UUID] = orm.mapped_column(nullable=True, index=True)
    source_type: orm.Mapped[SlackSourceType] = orm.mapped_column(nullable=False)
    source_id: orm.Mapped[str] = orm.mapped_column(nullable=False)
    created: orm.Mapped[datetime] = orm.mapped_column(nullable=False, default=datetime.utcnow)
    updated: orm.Mapped[datetime] = orm.mapped_column(nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


def upgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    teamstmt = select(eorm.TeamOrm)
    team = session.scalars(teamstmt).one()

    stmt1 = select(DocumentOrm)
    results1 = session.scalars(stmt1).all()

    for result in results1:
        if result.external_id is None or result.external_url is None:
            print("SKIPPING:", result.id)
            continue

        dr = eorm.DocumentReferenceOrm(
            team_id=team.id,
            document_id=result.external_id,
            document_url=result.external_url,
        )

        session.add(dr)
        session.commit()

        slacksubstmt = (
            select(SlackSubscriptionOrm)
            .where(SlackSubscriptionOrm.document_id == result.id)
        )

        subs = session.scalars(slacksubstmt).all()

        for sub in subs:
            abssub = eorm.SubscriptionOrm(
                team_id=team.id,
                source_platform=SubscriptionSourcePlatform.slack,
                source_event=SubscriptionSourceEvent.slack_message,
                source_id=sub.source_id,
                document_reference_id=dr.id,
            )
            session.add(abssub)

        session.commit()

def downgrade() -> None:
    pass
