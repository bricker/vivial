from eave.core.graphql.types.account import Account
import eave.core.internal.database
from starlette.requests import Request
from starlette.responses import Response

from eave.core.internal.orm.account import AccountOrm


async def login(email: str, plaintext_password: str) -> Account:
    async with eave.core.internal.database.async_session.begin() as db_session:
        account = await AccountOrm.one_or_exception(
            session=db_session,
            params=AccountOrm.QueryParams(
                auth=AccountOrm.AuthQueryParams(
                    email=email,
                    plaintext_password=plaintext_password,
                ),
            ),
        )

    return Account(
        id=account.id,
        email=account.email,
    )
