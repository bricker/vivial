import re
from .base_collector import BaseCollector
from .correlation_context import corr_ctx

user_table_name_patterns = [
    r"user$",
    r"users$",
    r"account$",
    r"accounts$",
]


columns_of_interest_patterns = [
    r"^id$",
    r"^uid$",
    r"^user_id$",
    r"^account_id$",
]


def is_user_table(table_name: str) -> bool:
    table = table_name.lower()
    for table_pattern in user_table_name_patterns:
        if re.search(table_pattern, table):
            return True
    return False


def is_field_of_interest(field_name: str) -> bool:
    field = field_name.lower()
    for col_pattern in columns_of_interest_patterns:
        if re.search(col_pattern, field):
            return True
    return False


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
