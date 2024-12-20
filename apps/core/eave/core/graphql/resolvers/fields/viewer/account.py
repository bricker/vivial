from datetime import UTC, datetime, timedelta
from uuid import UUID

import strawberry
import stripe

from eave.core import database
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.types.account import Account
from eave.core.graphql.types.activity import ActivityPlan
from eave.core.graphql.types.outing import (
    Outing,
)
from eave.core.graphql.types.restaurant import Reservation
from eave.core.graphql.types.survey import Survey
from eave.core.lib.event_helpers import get_activity, get_restaurant
from eave.core.orm.account import AccountOrm
from eave.core.orm.outing import OutingOrm
from eave.stdlib.util import unwrap


async def get_viewer_account_query(*, info: strawberry.Info[GraphQLContext]) -> Account:
    account_id = unwrap(info.context.get("authenticated_account_id"))

    async with database.async_session.begin() as db_session:
        account_orm = await AccountOrm.get_one(db_session, account_id)

    return Account.from_orm(account_orm)
