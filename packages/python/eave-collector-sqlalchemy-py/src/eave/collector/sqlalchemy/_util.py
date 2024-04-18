import re


LEADING_COMMENT_REMOVER_RE = re.compile(r"^/\*.*?\*/")

def operation_name(statement: str) -> str | None:
    parts = LEADING_COMMENT_REMOVER_RE.sub("", statement).split()
    if len(parts) == 0:
        return None
    else:
        return parts[0]
