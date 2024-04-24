from inspect import Parameter, signature
from typing import Any, Callable


def normalized_args(func: Callable[..., object], args: tuple[object, ...], kwargs: dict[str, object]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}

    sig = signature(func)
    for idx, (name, parameter) in enumerate(sig.parameters.items()):
        match parameter.kind:
            case Parameter.POSITIONAL_ONLY:
                if idx < len(args):
                    normalized[name] = args[idx]
                else:
                    normalized[name] = Parameter.empty

            case Parameter.KEYWORD_ONLY:
                if name in kwargs:
                    normalized[name] = kwargs[name]
                else:
                    normalized[name] = Parameter.empty

            case Parameter.POSITIONAL_OR_KEYWORD:
                if name in kwargs:
                    normalized[name] = kwargs[name]
                elif idx < len(args):
                    normalized[name] = args[idx]
                else:
                    normalized[name] = Parameter.empty

            case Parameter.VAR_POSITIONAL:
                # FIXME: This should remove anything that isn't named in the signature
                normalized["*args"] = args

            case Parameter.VAR_KEYWORD:
                # FIXME: This should remove anything that isn't named in the signature
                normalized["**kwargs"] = kwargs

            case _:
                pass

    return normalized
