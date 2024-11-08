from uuid import UUID, uuid4

import strawberry

from ..types.account import Account, UpdateAccountInput, UpdateAccountSuccess
from ..types.category import Category
from ..types.preferences import Preferences

MOCK_ACCOUNT = Account(
    first_name="Lana",
    last_name="Nguyen",
    email="lana@vivialapp.com",
    phone_number="(555) 555-5555",
    preferences=Preferences(
        open_to_bars=True,
        requires_wheelchair_accessibility=False,
        restaurant_categories=[Category(id=uuid4(), label="Mexican", is_default=True)],
        activity_categories=[
            Category(id=uuid4(), label="Music", subcategory_id=uuid4(), subcategory_label="EDM", is_default=True)
        ],
    ),
)


async def update_account_mutation(*, info: strawberry.Info, input: UpdateAccountInput) -> UpdateAccountSuccess:
    return UpdateAccountSuccess(account=MOCK_ACCOUNT)


async def account_query(*, info: strawberry.Info, account_id: UUID) -> Account:
    # TODO: Fetch account by account_id.
    return MOCK_ACCOUNT
