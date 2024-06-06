import re
from typing import Any

from .base_collector import BaseCollector
from .correlation_context import corr_ctx

user_table_name_patterns = [
    r"users?$",
    r"accounts?$",
]

primary_key_patterns = [
    r"^id$",
    r"^uid$",
]

foreign_key_patterns = [
    r"_id$",
    r"Id$",  # TODO: enforce some lower letter comes before?
    r"-id$",
]


def is_user_table(table_name: str) -> bool:
    table = table_name.lower()
    return any(re.search(table_pattern, table) for table_pattern in user_table_name_patterns)


def save_identification_data(table_name: str, column_value_map: dict[str, Any]) -> None:
    """
    Given table schema info and values mapped by column, persist data to
    correlation context that relate to user identificiation (primary/foreign keys).

    Based on the assumption that relations we want to track (like team/org/group ID)
    will have a 1-to-many relation with the users table, and each user row will have
    a column containing a foreign key value we will want to persist (likely matching
    the pattern *_id).

        Parameters:
            table_name (str): name of database table
            column_value_map (dict[str, str]): mapping from column name to value
    """
    if is_user_table(table_name):
        for key, value in column_value_map.items():
            lower_key = key.lower()
            if any(re.search(pat, lower_key) for pat in primary_key_patterns):
                corr_ctx.set("account_id", str(value))
                continue
            # casing matters for matching camelCase, so no lower_key
            if any(re.search(pat, key) for pat in foreign_key_patterns):
                corr_ctx.set(key, str(value))
                continue


class BaseDatabaseCollector(BaseCollector):
    pass
