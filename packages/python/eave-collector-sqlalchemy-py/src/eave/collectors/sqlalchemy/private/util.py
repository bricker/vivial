import re
from typing import Literal

from wrapt import ObjectProxy

LEADING_COMMENT_REMOVER_RE = re.compile(r"^/\*.*?\*/")


def operation_name(statement: str) -> str | None:
    parts = LEADING_COMMENT_REMOVER_RE.sub("", statement).split()
    if len(parts) == 0:
        return None
    else:
        return parts[0]

def normalize_vendor(vendor: str) -> str:
    """Return a canonical name for a type of database."""
    if "sqlite" in vendor:
        return "sqlite"

    if "postgres" in vendor or vendor == "psycopg2":
        return "postgresql"

    return vendor
