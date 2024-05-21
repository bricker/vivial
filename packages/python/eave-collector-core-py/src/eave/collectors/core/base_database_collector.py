from typing import Any
from .base_collector import BaseCollector
from .correlation_context import corr_ctx

tables_of_interest = {
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

def save_identification_data(table_name: str, primary_keys: list[Any]) -> None:
    """
    Saves into correlation context global any database values that may be useful for
    user identification.

        Parameters:
            table_name (str): name of the `data` entry's table
            data (dict): key-value map of a table entry's keys and values
    """

    if len(primary_keys) == 0:
        return

    if table_name.lower() in tables_of_interest:
        user_id = primary_keys[0]
        corr_ctx.set("user_id", str(user_id))

    # for key, value in data.items():
    #     if key.lower() in keys_of_interest:

    #         # accounts_id = abc123
    #         corr_ctx.set(f"{table_name}_{key}".lower(), value)



class BaseDatabaseCollector(BaseCollector):
    pass
