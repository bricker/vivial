from typing import Any
from .base_collector import BaseCollector
from .correlation_context import corr_ctx

user_table_names = {
    "user",
    "users",
    "account",
    "accounts",
}


keys_of_interest = {
    "id",
    "uid",
    "user_id",
    "account_id",
}


def is_user_table(table_name: str) -> bool:
    # TODO: what about grouped table names, like in bq? (e.g. "production.core-db.accounts")
    return table_name.lower() in user_table_names


def is_field_of_interest(field_name: str) -> bool:
    # TODO: "accounts.id"
    return field_name.lower() in keys_of_interest


def save_identification_data(table_name: str, primary_keys: list[Any]) -> None:
    """
    Saves into correlation context global any database values that may be useful for
    user identification.

        Parameters:
            table_name (str): name of database table
            primary_keys (list): primary key value(s) for relevant row(s) in `table_name`
    """

    if len(primary_keys) == 0:
        return

    if is_user_table(table_name):
        user_id = primary_keys[0]
        corr_ctx.set("user_id", str(user_id))


class BaseDatabaseCollector(BaseCollector):
    pass
