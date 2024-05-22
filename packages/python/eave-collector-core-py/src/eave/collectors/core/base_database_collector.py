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
    # TODO: what about grouped table names, like "production.core-db.accounts"
    return table_name.lower() in user_table_names


def is_field_of_interest(field_name: str) -> bool:
    return field_name.lower() in keys_of_interest


def save_identification_data(table_name: str, primary_key: str) -> None:
    """
    Saves into correlation context global any database values that may be useful for
    user identification.

        Parameters:
            table_name (str): name of database table
            primary_key (str): primary key value for relevant row in `table_name`
    """
    if is_user_table(table_name):
        corr_ctx.set("user_id", primary_key)


class BaseDatabaseCollector(BaseCollector):
    pass
