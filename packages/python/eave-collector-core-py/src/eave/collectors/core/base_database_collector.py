import re

from .base_collector import BaseCollector
from .correlation_context import corr_ctx

# no start string matcher ^ because names may have path prefix
# (e.g. production.coredb.users)
common_tables_of_interest_patterns = [
    r"users?$",
    r"accounts?$",
]

# TODO: load from network
extended_tables_of_interest_patterns = []


common_columns_of_interest_patterns = [
    r"^id$",
    r"^uid$",
    r"^user_id$",
    r"^account_id$",
]

# TODO: from network
extended_columns_of_interest_patterns = []


def is_table_of_interest(table_name: str) -> bool:
    table = table_name.lower()
    for table_pattern in common_tables_of_interest_patterns + extended_tables_of_interest_patterns:
        if re.search(table_pattern, table):
            return True
    return False


def is_column_of_interest(column_name: str) -> bool:
    column = column_name.lower()
    for col_pattern in common_columns_of_interest_patterns + extended_columns_of_interest_patterns:
        if re.search(col_pattern, column):
            return True
    return False


def save_data_of_interest(table_name: str, column_name: str, column_value: str) -> None:
    """
    Saves into correlation context global any value where the provided table column
    is of interest (usually for user identification).

        Parameters:
            table_name (str): name of database table
            column_name (str): name of table column
            column_value (str): primary key value for relevant row in `table_name`
    """
    if is_table_of_interest(table_name) and is_column_of_interest(column_name):
        corr_ctx.set(f"{table_name}_{column_name}", column_value)


class BaseDatabaseCollector(BaseCollector):
    pass
