from eave.core.graphql.enums import Client
from eave.core.graphql.types.account import Account
import eave.core.internal.database
from starlette.requests import Request
from starlette.responses import Response

from eave.core.internal.orm.account import AccountOrm
from eave.core.internal.orm.auth_token import AuthTokenOrm


async def login(*, email: str, plaintext_password: str) -> Account:
    async with eave.core.internal.database.async_session.begin() as db_session:
        account = await AccountOrm.one_or_exception(
            session=db_session,
            params=AccountOrm.QueryParams(
                email=email,
            ),
        )

        if account.validate_password_or_exception(plaintext_password):
            auth_token = await AuthTokenOrm.create(
                session=db_session,
                account_id=account.id,
            )

    return Account(
        id=account.id,
        email=account.email,
    )

async def logout() -> None:
    pass