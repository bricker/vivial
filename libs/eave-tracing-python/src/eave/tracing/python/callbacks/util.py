import sys
from datetime import datetime, date

DISABLE = sys.monitoring.DISABLE

# FIXME: support list, tuple, and dict; may contain unpickleable objects.
PRIMITIVE_TYPES = (bool, str, int, float, date, datetime, type(None))

_builtins_set = set(sys.builtin_module_names)
_stdlib_set = sys.stdlib_module_names
_common_noisy_modules_to_ignore = set(
    (
        "pydantic",
        "pkg_resources",
    )
)

_ignore_modules_set = _builtins_set | _stdlib_set | _common_noisy_modules_to_ignore


def should_ignore_module(name: str | None, scope: str | None) -> bool:
    if not name:
        return False

    elif name in _ignore_modules_set:
        return True

    elif name.startswith("_"):
        # ignore "private" modules, eg "_pytest"
        # TODO: Is this okay?
        return True

    elif scope and not name.startswith(scope):
        # A scope was provided; if the code's module isn't within the scope, bypass
        return True

    else:
        return False
