from typing import Any
from .async_task import AsyncioCorrelationContext as AsyncioCorrelationContext
from .thread import ThreadedCorrelationContext as ThreadedCorrelationContext

# TODO: figure out which ctx storage type we need at runtime?
corr_ctx = ThreadedCorrelationContext()


def save_identification_data(table_name: str, data: dict[str, Any]) -> None:
    """
    Saves into correlation context global any database values that may be useful for
    user identification.

        Parameters:
            table_name (str): name of the `data` entry's table
            data (dict): key-value map of a table entry's keys and values
    """
    tables_of_interest = {
        "user",
        "users",
        "account",
        "accounts",
    }

    if table_name.lower() not in tables_of_interest:
        return

    keys_of_interest = {
        "id",
        "uid",
    }

    for key, value in data.items():
        if key.lower() in keys_of_interest:
            corr_ctx.set(f"{table_name}_{key}".lower(), value)
