import strawberry

from ..inputs.account import UpdateAccountInput


async def update_account_mutation(*, info: strawberry.Info, input: UpdateAccountInput) -> bool:
    return True
